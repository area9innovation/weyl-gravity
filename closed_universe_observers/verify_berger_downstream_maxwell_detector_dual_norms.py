#!/usr/bin/env python3
"""Verify the Berger downstream Maxwell detector dual-norm certificate."""

import json
from fractions import Fraction

from closed_universe_observers.generate_berger_downstream_maxwell_detector_dual_norms import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    rows = value["detector_dual_norms"]
    assert [row["detector_id"] for row in rows] == ["D0", "D1"]
    assert Fraction(rows[1]["spatial_profile_L2_norm_squared_upper"]) == Fraction(40, 9) * Fraction(
        rows[0]["spatial_profile_L2_norm_squared_upper"]
    )
    assert len(value["retarded_energy_composition"]["four_channel_bounds"]) == 4
    assert value["flags"]["FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED"] is False
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger downstream Maxwell detector dual-norm verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
