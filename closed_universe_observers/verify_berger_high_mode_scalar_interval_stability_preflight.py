#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_high_mode_scalar_interval_stability_preflight import (
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
    sentinels = {row["two_j"]: row for row in value["sentinel_audits"]}
    assert Fraction(sentinels[140]["raw_width"]) < Fraction(1, 1000)
    assert Fraction(sentinels[256]["raw_width"]) > 10**8
    assert sentinels[256]["unit_bound_intersection"] == ["-1", "1"]
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False


def main() -> int:
    verify(json.loads(CERTIFICATE.read_text()))
    print("high-mode scalar interval-stability preflight verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
