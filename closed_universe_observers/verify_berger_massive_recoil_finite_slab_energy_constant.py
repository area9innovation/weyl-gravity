#!/usr/bin/env python3
"""Verify the generated Berger massive finite-slab recoil constant."""

import json
from fractions import Fraction

from closed_universe_observers.generate_berger_massive_recoil_finite_slab_energy_constant import (
    CERTIFICATE,
    build,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    assert value["massive_energy_theorem"]["sector_inverse"][1][1] == "1/m2"
    assert [row["switch_id"] for row in value["switch_constants"]] == ["h_0", "h_1"]
    assert Fraction(value["switch_constants"][0]["h_sup_upper"]) == 3 * Fraction(
        value["switch_constants"][1]["h_sup_upper"]
    )
    assert value["flags"]["DOWNSTREAM_MAXWELL_DETECTOR_DUAL_NORM_EXPORTED"] is False
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger massive recoil finite-slab energy verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
