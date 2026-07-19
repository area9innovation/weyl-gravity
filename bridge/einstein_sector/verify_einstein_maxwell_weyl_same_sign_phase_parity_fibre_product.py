"""Independent verifier for the six exact bounded phase/parity fibre products."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_phase_parity_fibre_product.json"
EXPECTED = {
    16: (20, 1, [12], "L3_candidate_16"),
    17: (20, 1, [14], "L1_candidate_17"),
    18: (30, 1, [22], "L3_candidate_18"),
    19: (30, 6, [10, 20], "L4_candidate_19"),
    20: (20, 1, [14], "L1_candidate_20"),
    21: (20, 4, [10], "L4_candidate_21"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify() -> None:
    payload = json.loads(CERT.read_text())
    schema_path = ROOT / payload["schema_path"]
    schema = json.loads(schema_path.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    assert payload["schema_sha256"] == sha(schema_path)
    assert payload["provenance"]["generator_sha256"] == sha(ROOT / payload["provenance"]["generator_path"])
    for item in payload["provenance"]["inputs"].values():
        assert item["sha256"] == sha(ROOT / item["path"])

    rows = payload["candidate_rows"]
    assert [row["candidate_index"] for row in rows] == list(range(16, 22))
    for row in rows:
        expected = EXPECTED[row["candidate_index"]]
        geometry = row["resonance_geometry"]
        assert geometry["ambient_dimension_over_C"] == expected[0]
        assert geometry["irreducible_components_over_C"] == expected[1]
        assert geometry["component_dimensions_over_C"] == expected[2]
        assert row["resonance_fibre_id"] == expected[3]
        formula = row["bounded_cone_formula"]
        assert formula["display"] == "Z_i^bounded = pi_i^{-1}(C_i) intersect mu_J^{-1}(0) intersect V(B_i)"
        assert "equivalent" in formula["necessity_and_sufficiency"]
        assert row["verdict"].endswith("REAL_COMPONENT_DECOMPOSITION_OPEN")

    flags = payload["classification"]
    assert flags["all_six_bounded_cones_have_exact_necessary_and_sufficient_equational_formulas"]
    assert flags["all_six_cross_fibre_complex_resonance_varieties_decomposed"]
    assert flags["all_relative_phases_and_both_parities_retained_in_formula"]
    assert not flags["all_six_real_hermitian_phase_parity_intersections_decomposed"]
    assert not flags["all_orders_integrability"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_PHASE_PARITY_FIBRE_PRODUCT verifier: PASS")


if __name__ == "__main__":
    verify()
