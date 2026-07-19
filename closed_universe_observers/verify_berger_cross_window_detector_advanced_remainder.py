#!/usr/bin/env python3
"""Verify the D1-to-h0 advanced-Maxwell remainder certificate."""

import json
from fractions import Fraction

from closed_universe_observers.generate_berger_cross_window_detector_advanced_remainder import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["cross_window"]["kernel_tau_interval"] == ["7/24", "3/8"]
    assert value["cross_window"]["T_interval"] == ["5/16", "17/48"]
    assert [row["two_j"] for row in value["mode_remainders"]] == list(range(5))
    assert all(
        Fraction(row["uniform_entire_series_remainders"]["tau_max"])
        == Fraction(3, 8)
        for row in value["mode_remainders"]
    )
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger cross-window detector advanced remainder verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
