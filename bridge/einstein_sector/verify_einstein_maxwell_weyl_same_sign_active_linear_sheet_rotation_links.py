"""Independent verifier for candidate-19/21 active linear-sheet rotation links."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_active_linear_sheet_rotation_links.json"


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

    theorem = payload["restricted_current_theorem"]
    assert theorem["all_six_active_linear_sheets_restricted_current_nondegenerate"]
    assert "(5,5,0)" in theorem["active_core_inertia"]
    assert "definite" in theorem["definite_subspace_lemma"]
    rotation = payload["rotation_link_theorem"]
    assert rotation["component_counts"] == {"candidate_19": 4, "candidate_21": 2}
    assert rotation["all_fixed_occupation_rotation_zero_links_nonempty"]
    assert rotation["all_fixed_occupation_rotation_zero_links_connected_componentwise"]
    assert "CP^4 x CP^4" in rotation["projective_model"]
    assert "Theorem 1.1(b)" in rotation["connectedness"]

    rows = payload["candidate_rows"]
    assert [row["candidate_index"] for row in rows] == [19, 21]
    assert [row["active_component_count"] for row in rows] == [4, 2]
    for row in rows:
        assert len(row["components"]) == row["active_component_count"]
        assert row["verdict"] == "ALL_ACTIVE_LINEAR_SHEET_ROTATION_LINKS_CONNECTED_COMPONENTWISE"
        for component in row["components"]:
            assert component["affine_complex_dimension"] == 10
            assert component["restricted_Hermitian_current_inertia"] == [5, 5, 0]
            assert component["fixed_resonant_norm_real_symplectic_dimension"] == 16
            assert component["rotation_zero_link"] == "NONEMPTY_AND_CONNECTED"
    flags = payload["classification"]
    assert flags["all_six_restricted_currents_nondegenerate"]
    assert flags["all_six_fixed_occupation_rotation_zero_links_connected_componentwise"]
    assert not flags["candidates17_18_20_active_varieties_classified"]
    assert not flags["occupation_strata_glued"]
    assert not flags["causal_residual_observational_or_quantum_claim"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_ACTIVE_LINEAR_SHEET_ROTATION_LINKS verifier: PASS")


if __name__ == "__main__":
    verify()
