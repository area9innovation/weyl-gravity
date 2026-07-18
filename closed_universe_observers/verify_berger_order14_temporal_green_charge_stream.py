#!/usr/bin/env python3
import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_order14_temporal_green_charge_stream import (
    CERTIFICATE,
    DEPENDENCIES,
    ROOT,
    SCHEMA,
    remainder_audits,
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
        assert reference["sha256"] == _sha256(path)
        assert reference["result_id"] == json.loads(path.read_text())["result_id"]
    for source in value["provenance"]["source_manifest"]:
        path = ROOT / source["path"]
        assert source["sha256"] == _sha256(path)
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["flags"]["ORDER14_TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED"] is True
    assert value["flags"]["ORDER14_TEMPORAL_GREEN_IMAGE_CERTIFIED"] is False
    assert value["remainder_audits"] == remainder_audits()
    assert len(value["mode_summaries"]) == 139
    assert value["mode_summaries"][0]["two_j"] == 0
    assert value["mode_summaries"][-1]["two_j"] == 138
    assert value["coverage"]["nonzero_detector_column_charge_block_count"] == sum(
        row["nonzero_detector_column_charge_block_count"] for row in value["mode_summaries"]
    )
    assert value["coverage"]["spatial_polynomial_coefficient_interval_count"] == sum(
        row["spatial_polynomial_coefficient_interval_count"] for row in value["mode_summaries"]
    )
    assert value["coverage"]["temporal_polynomial_coefficient_interval_count"] == sum(
        row["temporal_polynomial_coefficient_interval_count"] for row in value["mode_summaries"]
    )
    for row in value["remainder_audits"]:
        assert Fraction(row["cosine_geometric_ratio"]) < 1
        assert Fraction(row["sine_geometric_ratio"]) < 1
        assert Fraction(row["exact_cosine_error_absolute_lower"]) > 1


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    verify(value)
    print("order-14 temporal Green charge stream verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
