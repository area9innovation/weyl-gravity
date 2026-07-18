#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_jacobi_axial_stability_preflight import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
)


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(value: dict) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    for name, path in DEPENDENCIES.items():
        reference = value["dependency_refs"][name]
        assert reference["path"] == str(path.relative_to(ROOT))
        assert reference["result_id"] == json.loads(path.read_text())["result_id"]
        assert reference["sha256"] == _sha256(path)
    for source in value["provenance"]["source_manifest"]:
        assert source["sha256"] == _sha256(ROOT / source["path"])
    factorization = value["factorization"]
    assert factorization["low_rail_unique_diagonal_count"] == 4970
    assert factorization["coefficient_identity_comparison_count"] == 119280
    assert factorization["coefficient_identity_defect_count"] == 0
    sentinels = {row["two_j"]: row for row in value["axial_sentinel_audits"]}
    assert Fraction(sentinels[974]["partial_interval_width_lower"]) < Fraction(1, 10)
    assert Fraction(sentinels[975]["partial_interval_width_lower"]) > Fraction(1, 10)
    assert Fraction(sentinels[2047]["partial_interval_width_lower"]) > 1000
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["flags"]["CORRELATED_AXIAL_OSCILLATORY_EVALUATOR_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("Jacobi-axial stability preflight verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
