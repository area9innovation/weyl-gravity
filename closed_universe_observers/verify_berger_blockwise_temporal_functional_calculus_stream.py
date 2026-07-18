#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_blockwise_temporal_functional_calculus_stream import (
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
        path = ROOT / source["path"]
        assert source["sha256"] == _sha256(path)
    assert value["atlas_status"] == "CERTIFIED"
    assert len(value["mode_summaries"]) == 139
    for field in (
        "populated_detector_column_charge_block_count",
        "spatial_microphase_dressed_amplitude_interval_count",
        "temporal_microphase_dressed_amplitude_interval_count",
    ):
        assert value["coverage"][field] == sum(row[field] for row in value["mode_summaries"])
    for row in value["uniform_error_budgets"]:
        assert Fraction(row["spatial_exact_T_image_remainder_upper"]) < Fraction(1, 10**17)
        assert Fraction(row["temporal_exact_T_image_remainder_upper"]) < Fraction(1, 10**15)
    assert value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] is False


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    verify(value)
    print("blockwise temporal functional-calculus stream verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
