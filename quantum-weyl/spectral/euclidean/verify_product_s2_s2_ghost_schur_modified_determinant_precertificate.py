#!/usr/bin/env python3
"""Independent verifier for the product Schur determinant assembly."""

from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import mpmath as mp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/PRODUCT_S2_S2_GHOST_SCHUR_MODIFIED_DETERMINANT_PRECERTIFICATE.json"
SCHEMA = HERE / "schema/product-s2-s2-ghost-schur-modified-determinant-precertificate-v1.schema.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    payload = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(payload)
    sources = {}
    for name, reference in payload["dependencies"].items():
        path = ROOT / reference["path"]
        assert path.is_file()
        assert _sha256(path) == reference["sha256"]
        sources[name] = json.loads(path.read_text())
        assert sources[name]["result_id"] == reference["result_id"]

    det3 = sources["det3"]["det3_enclosure"]
    split = sources["weighted_rows"]["weighted_rows"]["low_order_split_R_K_minus_half_R_K2"]
    rows = payload["directed_enclosures"]
    with localcontext() as context:
        context.prec = 90
        direct_regular_lower = Decimal(det3["lower_endpoint_decimal"]) + Decimal(split["lower"])
        direct_regular_upper = Decimal(det3["upper_endpoint_decimal"]) + Decimal(split["upper"])
    stored_regular = rows["regular_modified_determinant"]
    assert Decimal(stored_regular["lower"]) <= direct_regular_lower
    assert Decimal(stored_regular["upper"]) >= direct_regular_upper

    mp.mp.dps = 100
    log_factor = 6 * mp.log(3)
    stored_exceptional = rows["matched_exceptional_log"]
    assert Decimal(stored_exceptional["lower"]) < Decimal(str(-log_factor))
    assert Decimal(stored_exceptional["upper"]) > Decimal(str(-log_factor))
    stored_coupled = rows["coupled_schur_log"]
    assert Decimal(stored_coupled["lower"]) <= Decimal(stored_regular["lower"]) + Decimal(stored_exceptional["lower"])
    assert Decimal(stored_coupled["upper"]) >= Decimal(stored_regular["upper"]) + Decimal(stored_exceptional["upper"])
    assert Decimal(stored_coupled["upper"]) - Decimal(stored_coupled["lower"]) < Decimal("5.6e-8")

    blocker = payload["tier3_blocker"]
    assert blocker == {
        "command": "PYTHONPATH=quantum-weyl python3 -m unittest discover -s quantum-weyl -p 'test_*.py' -q",
        "tests_run": 830,
        "elapsed_seconds": "629.08",
        "failures": 20,
        "errors": 12,
        "failure_scopes": ["cartan", "relative", "lorentzian", "transfer"],
        "spectral_package_failures": 0,
        "status": "FAILED_NOT_A_PASS",
    }
    flags = payload["claim_flags"]
    assert flags["MATCHED_EXCEPTIONAL_COUPLED_SCHUR_ENCLOSURE_DERIVED"] is True
    assert flags["PRODUCT_WEIGHTED_R_K_COMPUTED"] is False
    assert flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"] is False
    assert flags["LORENTZIAN_CERTIFIED"] is False
    print("PRODUCT S2xS2 SCHUR MODIFIED DETERMINANT: INDEPENDENT PRECERTIFICATE PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
