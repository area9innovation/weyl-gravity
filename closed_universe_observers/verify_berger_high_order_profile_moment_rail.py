#!/usr/bin/env python3
"""Verify the validated high-order Berger profile-moment rail."""

import hashlib
import json
from fractions import Fraction

from closed_universe_observers.generate_berger_high_order_profile_moment_rail import (
    CERTIFICATE,
    MAX_K,
    ROOT,
    build,
    clock_secant_moments,
    radial_moments,
)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    assert value == build()
    radial = radial_moments()
    clock = clock_secant_moments()
    assert len(radial) == len(clock) == MAX_K + 1
    assert radial[0] == clock[0] == (Fraction(1), Fraction(1))
    assert all(0 <= lower <= upper <= 1 for lower, upper in radial)
    assert all(0 < clock[k][0] <= clock[k][1] and clock[k][1] > 1 for k in range(1, MAX_K + 1))
    assert value["low_order_compatibility_audit"]["radial_containment_defect_count"] == 0
    assert value["low_order_compatibility_audit"]["clock_containment_defect_count"] == 0
    assert value["flags"]["HIGH_MODE_SCALAR_COEFFICIENT_VALUES_EVALUATED"] is False
    for evidence in value["dependency_refs"].values():
        path = ROOT / evidence["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence["sha256"]
        assert json.loads(path.read_text())["result_id"] == evidence["result_id"]
    print("BERGER_HIGH_ORDER_PROFILE_MOMENT_RAIL verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
