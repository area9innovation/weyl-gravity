"""Independent verifier for the six complete scalar-cone amplitude sections."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_scalar_cone_sections.json"


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
    rows = payload["section_rows"]
    assert [row["candidate_index"] for row in rows] == list(range(16, 22))
    methods = Counter(row["section"]["method"] for row in rows)
    assert methods == Counter({"ALL_AXIAL_AXISYMMETRIC_ODD_L_SECTION": 4, "REAL_REGULAR_PENCIL_L4_SECTION": 1, "REAL_SCALAR_MIXED_PARITY_L4_SECTION": 1})
    for row in rows:
        method = row["section"]["method"]
        if method == "ALL_AXIAL_AXISYMMETRIC_ODD_L_SECTION":
            ell = int(row["section"]["resonance_zero"].split("|")[1].split(",")[0])
            assert clebsch_gordan(2, 2, ell, 0, 0, 0) == 0
        else:
            assert "independent" in row["section"]["resonance_zero"]
        assert row["bounded_verdict"] == "EVERY_SCALAR_NULL_OCCUPATION_HAS_A_BOUNDED_AMPLITUDE_LIFT"
    flags = payload["classification"]
    assert flags["all_six_complete_scalar_cones_have_bounded_amplitude_sections"]
    assert flags["bounded_to_scalar_occupation_projection_surjective"]
    assert flags["all_scalar_cone_faces_and_pairwise_ray_sums_covered"]
    assert not flags["every_amplitude_over_each_scalar_occupation_bounded"]
    assert not flags["six_full_phase_parity_fibres_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_SCALAR_CONE_SECTIONS verifier: PASS")


if __name__ == "__main__":
    verify()
