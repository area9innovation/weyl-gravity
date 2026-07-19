"""Independent structural verifier for all 24 same-sign extreme-ray lifts."""

import hashlib
import json
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator
from sympy.physics.wigner import clebsch_gordan


ROOT = Path(__file__).resolve().parents[2]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_same_sign_extreme_ray_lifts.json"


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
    rows = payload["lift_rows"]
    assert len(rows) == 24
    assert Counter(row["candidate_index"] for row in rows) == Counter({index: 4 for index in range(16, 22)})
    assert Counter(row["ray_id"] for row in rows) == Counter({f"R{index}": 6 for index in range(1, 5)})
    methods = Counter(row["cross_fibre_disposition"]["method"] for row in rows)
    assert methods == Counter(payload["summary"]["disposition_counts"])
    assert methods == Counter({"RESONANT_FACTOR_ABSENT": 10, "AXISYMMETRIC_ODD_L_ZERO": 10, "REAL_REGULAR_PENCIL_L4_COMPONENT": 2, "REAL_SCALAR_MIXED_PARITY_L4_COMPONENT": 2})
    for row in rows:
        method = row["cross_fibre_disposition"]["method"]
        if method == "RESONANT_FACTOR_ABSENT":
            assert row["cross_fibre_disposition"]["missing_nodes"]
        elif method == "AXISYMMETRIC_ODD_L_ZERO":
            ell = int(row["cross_fibre_disposition"]["clebsch_gordan"].split("|")[1].split(",")[0])
            assert ell in (1, 3) and clebsch_gordan(2, 2, ell, 0, 0, 0) == 0
        else:
            assert row["candidate_index"] in (19, 21)
            assert "independently" in row["cross_fibre_disposition"]["independent_scaling"]
        assert row["bounded_verdict"] == "EXTREME_RAY_LIFTS_TO_NONZERO_Z2_BOUNDED_POINT"
    flags = payload["classification"]
    assert flags["all_24_scalar_extreme_rays_have_nonzero_bounded_lifts"]
    assert not flags["arbitrary_nonnegative_sums_of_lifts_classified"]
    assert not flags["six_full_real_bounded_cones_classified"]
    print("EINSTEIN_MAXWELL_WEYL_SAME_SIGN_EXTREME_RAY_LIFTS verifier: PASS")


if __name__ == "__main__":
    verify()
