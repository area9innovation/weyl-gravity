#!/usr/bin/env python3
"""Verify the adaptive Peter--Weyl route preflight independently."""

import hashlib
import json
from fractions import Fraction

from closed_universe_observers.generate_berger_adaptive_peter_weyl_route_preflight import (
    CERTIFICATE,
    ROOT,
    build,
    weighted_capacity,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    row = next(row for row in value["necessary_cutoffs"] if row["fraction_of_certified_energy_lower"] == "99/100")
    energy = Fraction(value["capacity_convention"]["profile_energy_lower"])
    target = Fraction(99, 100) * energy
    assert row["minimum_max_dimension_for_capacity"] == 139
    assert row["minimum_two_j_max_for_capacity"] == 138
    assert weighted_capacity(138) < target <= weighted_capacity(139)
    assert value["flags"]["TWO_J138_CONVERGENCE_CERTIFIED"] is False
    assert value["flags"]["BERGER_PHYSICAL_BRANCH_TO_DETECTOR_MAP_CERTIFIED"] is False
    for evidence in value["dependency_refs"].values():
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print("BERGER_ADAPTIVE_PETER_WEYL_ROUTE_PREFLIGHT verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
