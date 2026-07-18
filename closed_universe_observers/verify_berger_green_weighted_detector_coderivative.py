#!/usr/bin/env python3
"""Independently verify the green-weighted detector-coderivative artifact."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    CERTIFICATE, ROOT, build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert [row["detector_id"] for row in value["detectors"]] == ["D0", "D1"]
    assert all([mode["two_j"] for mode in row["modes"]] == list(range(5)) for row in value["detectors"])
    assert all(Fraction(mode["uniform_entire_series_remainders"]["spatial_cosine_entry_remainder_upper"]) >= 0 for row in value["detectors"] for mode in row["modes"])
    assert all(Fraction(mode["uniform_entire_series_remainders"]["temporal_sine_entry_remainder_upper"]) >= 0 for row in value["detectors"] for mode in row["modes"])
    assert value["coderivative_and_integration_by_parts"]["boundary_term_zero"] is True
    assert value["flags"]["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_BOUND_EXPORTED"] is False
    for row in value["dependency_refs"].values():
        path = ROOT / row["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"]
        assert json.loads(path.read_text())["result_id"] == row["result_id"]
    print("BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
