#!/usr/bin/env python3
"""Verify the clock-uniform Berger profile Sobolev N=1 certificate."""
from __future__ import annotations

import json

from closed_universe_observers.generate_berger_clock_uniform_profile_sobolev_n1 import CERTIFICATE, build


def main() -> int:
    stored = json.loads(CERTIFICATE.read_text())
    rebuilt = build()
    if stored != rebuilt:
        raise AssertionError("clock-uniform profile Sobolev N1 certificate is stale")
    if stored["operator_audit"]["scalar_coordinate_defect_count"] or stored["operator_audit"]["d_Delta_equals_Delta_d_defect_count"]:
        raise AssertionError("physical-space operator audit failed")
    if not all(row["small_tail_certified"] is False for row in stored["polarization_bounds"]):
        raise AssertionError("coarse N1 bound was promoted to a small-tail theorem")
    flags = stored["flags"]
    if flags["VALIDATED_INFINITE_SPATIAL_MODE_TAIL_UPPER_BOUND_EXPORTED"] is not True or flags["FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED"] is not False:
        raise AssertionError("tail/full-image lifecycle boundary drifted")
    print("clock-uniform Berger profile Sobolev N1 verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
