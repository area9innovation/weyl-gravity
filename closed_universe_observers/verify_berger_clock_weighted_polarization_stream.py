#!/usr/bin/env python3
"""Verify the detector-prefactored Berger polarization stream."""

import hashlib
import json
from fractions import Fraction

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_clock_weighted_polarization_stream import (
    CERTIFICATE,
    ROOT,
    SCHEMA,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    assert value == build()
    coverage = value["coverage"]
    assert coverage["detector_component_entry_count"] == 86736
    assert coverage["detector_component_scalar_term_application_count"] == 231018
    assert coverage["clock_power_interval_count"] == 520416
    assert [(row["two_j"], row["dimension"]) for row in value["mode_summaries"]] == [
        (two_j, two_j + 1) for two_j in range(139)
    ]
    assert value["direct_low_mode_compatibility_audit"] == {
        "audited_two_j_maximum": 4,
        "interval_comparison_count": 1980,
        "nonoverlap_defect_count": 0,
    }
    assert all(Fraction(width)>0 for width in value["maximum_interval_width_by_clock_power"].values())
    for evidence in value["dependency_refs"].values():
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    assert value["flags"]["TEMPORAL_GREEN_CHARGE_BLOCKS_APPLIED"] is False
    print("BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138 verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
