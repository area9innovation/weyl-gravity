#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_correlated_central_scalar_evaluator import (
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
    assert value["coverage"]["evaluated_even_mode_count"] == 1025
    assert value["coverage"]["low_rail_overlap_count"] == 70
    assert value["coverage"]["low_rail_overlap_defect_count"] == 0
    sentinels = {row["two_j"]: row for row in value["sentinel_audits"]}
    assert Fraction(sentinels[256]["interval"]["width"]) < Fraction(1, 1000)
    assert Fraction(sentinels[2048]["interval"]["width"]) < Fraction(1, 10)
    assert value["atlas_status"] == "CERTIFIED"
    assert value["flags"]["ALL_DIAGONALS_AND_CLOCK_POWERS_EVALUATED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("correlated central scalar evaluator verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
