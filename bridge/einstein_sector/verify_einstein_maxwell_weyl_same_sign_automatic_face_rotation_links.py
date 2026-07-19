"""Independent verifier for automatic-face rotation-zero connectedness."""

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_automatic_face_rotation_links.json"
EXPECTED_FACES = {
    16: [],
    17: ["R1", "R2"],
    18: ["R2", "R4"],
    19: ["R2", "R4"],
    20: ["R1", "R3"],
    21: ["R1", "R3"],
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

    theorem = payload["theorem"]
    assert theorem["external_theorem"]["doi"] == "10.1016/S0040-9383(97)00030-X"
    assert "proper moment map" in theorem["external_theorem"]["theorem"]
    rows = payload["candidate_rows"]
    assert [row["candidate_index"] for row in rows] == list(range(16, 22))
    for row in rows:
        index = row["candidate_index"]
        assert row["automatic_face"]["ray_generators"] == EXPECTED_FACES[index]
        if index == 16:
            assert row["verdict"] == "NOT_APPLICABLE"
        else:
            assert row["verdict"] == "CONNECTED_ON_EVERY_NONZERO_FIXED_OCCUPATION_SUPPORT_STRATUM"
            assert "compact connected product" in row["node_phase_reduction"]
            assert "negative q_minus" in row["symplectic_form"]
            assert "compact" in row["properness"]
            assert "axisymmetric" in row["nonemptiness"]
            assert "Theorem 1.1(b)" in row["connectedness"]
    flags = payload["classification"]
    assert flags["candidates_17_through_21_automatic_faces_classified"]
    assert flags["all_nonzero_fixed_occupation_rotation_zero_links_nonempty"]
    assert flags["all_nonzero_fixed_occupation_rotation_zero_links_connected"]
    assert not flags["active_resonance_strata_classified"]
    assert not flags["singular_strata_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_AUTOMATIC_FACE_ROTATION_LINKS verifier: PASS")


if __name__ == "__main__":
    verify()
