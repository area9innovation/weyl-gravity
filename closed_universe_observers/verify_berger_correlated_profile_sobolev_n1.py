#!/usr/bin/env python3
"""Verify the correlated Berger detector-profile Sobolev N=1 certificate."""
from __future__ import annotations

from fractions import Fraction
import json

from closed_universe_observers.generate_berger_correlated_profile_sobolev_n1 import CERTIFICATE, build


def main() -> int:
    stored = json.loads(CERTIFICATE.read_text())
    rebuilt = build()
    if stored != rebuilt:
        raise AssertionError("correlated profile Sobolev N1 certificate is stale")
    for row in stored["polarization_bounds"]:
        if row["angular_reduction"]["radial_interval_term_count"] != 21:
            raise AssertionError("angular reduction is incomplete")
        if Fraction(row["tail_L2_upper_after_two_j1024"]) >= Fraction(row["prior_triangle_tail_upper"]):
            raise AssertionError("correlated enclosure did not improve the prior rail")
        if row["small_tail_certified"] is not False:
            raise AssertionError("non-small N1 enclosure was promoted")
    flags = stored["flags"]
    if flags["TRUE_TAIL_OBSTRUCTED"] is not False or flags["FULL_ADVANCED_MAXWELL_GREEN_IMAGE_EVALUATED"] is not False:
        raise AssertionError("fail-closed tail lifecycle drifted")
    print("correlated Berger profile Sobolev N1 verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
