#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_correlated_axial_oscillatory_evaluator import (
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
    assert len(value["low_rail_audits"]) == 5
    assert all(row["published_interval_overlap"] for row in value["low_rail_audits"])
    high = {row["two_j"]: row for row in value["high_axial_sentinel_audits"]}
    assert set(high) == {975, 2047}
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in high.values())
    assert Fraction(value["resolution_mutation"]["coarse_interval"]["width"]) > Fraction(1, 10)
    assert value["resolution_mutation"]["detected"] is True
    assert value["atlas_status"] == "CERTIFIED"
    assert value["flags"]["COMPLETE_AXIAL_RAIL_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("correlated axial oscillatory evaluator verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
