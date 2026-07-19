"""Independent verifier for the six same-sign bounded witnesses."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_collision_bounded_witnesses.json"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])
    scalar_path = ROOT / payload["provenance"]["inputs"]["scalar_classifier"]["path"]
    scalar = json.loads(scalar_path.read_text())
    scalar_rows = {row["candidate_index"]: row for row in scalar["candidate_rows"]}
    candidate21_path = ROOT / payload["provenance"]["inputs"]["candidate21"]["path"]
    candidate21 = json.loads(candidate21_path.read_text())
    candidate21_decomposition = candidate21["decompositions"]
    if isinstance(candidate21_decomposition, dict):
        candidate21_decomposition = next(
            item for item in candidate21_decomposition.values()
            if isinstance(item, dict) and item.get("candidate_index") == 21
        )
    else:
        candidate21_decomposition = next(item for item in candidate21_decomposition if item["candidate_index"] == 21)
    mixed_plus = next(
        item for item in candidate21_decomposition["irreducible_components_over_C"]
        if item["component_id"] == "mixed_plus"
    )

    rows = payload["witness_rows"]
    assert [row["candidate_index"] for row in rows] == list(range(16, 22))
    expected_methods = {
        16: "AXISYMMETRIC_ODD_L_ZERO",
        17: "RESONANT_FACTOR_ABSENT",
        18: "RESONANT_FACTOR_ABSENT",
        19: "RESONANT_FACTOR_ABSENT",
        20: "AXISYMMETRIC_ODD_L_ZERO",
        21: "REAL_MIXED_PARITY_L4_COMPONENT",
    }
    for row in rows:
        index = row["candidate_index"]
        support = [(int(item["signed_momentum_n"]), item["branch"]) for item in row["support"]]
        weights = row["positive_absolute_current_occupations"]
        assert len(support) == len(weights) == 4
        assert row["rho"] == scalar_rows[index]["rho"]
        assert row["support"] == scalar_rows[index]["support"]
        assert weights == scalar_rows[index]["positive_weights"]
        disposition = row["cross_fibre_resonance"]
        assert disposition["method"] == expected_methods[index]
        isolated = row["isolated_resonance_crosswalk"]
        resonant_pair = [(1, isolated["first_branch"]), (2, isolated["second_branch"])]
        if disposition["method"] == "RESONANT_FACTOR_ABSENT":
            assert any(item not in support for item in resonant_pair)
        elif disposition["method"] == "AXISYMMETRIC_ODD_L_ZERO":
            assert isolated["output_ell"] in (1, 3)
            assert clebsch_gordan(2, 2, isolated["output_ell"], 0, 0, 0) == 0
        else:
            assert index == 21 and isolated["output_ell"] == 4
            assert disposition["r"] == mixed_plus["r"] and disposition["s"] == mixed_plus["s"]
            assert candidate21_decomposition["r_squared_interval"]["positive"]
            assert "kappa_A(r)" in disposition["amplitude_factorization"]
            assert "kappa_B(s)>0" in disposition["amplitude_factorization"]
        assert row["bounded_verdict"] == "NONZERO_POINT_IN_Z2_BOUNDED_CERTIFIED"

    flags = payload["classification"]
    assert flags["all_six_nonzero_bounded_points_certified"]
    assert not flags["all_six_complete_bounded_cones_classified"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_COLLISION_BOUNDED_WITNESSES verifier: PASS")


if __name__ == "__main__":
    verify()
