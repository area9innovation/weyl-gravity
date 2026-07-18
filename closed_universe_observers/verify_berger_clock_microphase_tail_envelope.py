#!/usr/bin/env python3
"""Verify the Berger clock-microphase tail-envelope certificate."""
from __future__ import annotations

from fractions import Fraction
import json

from closed_universe_observers.generate_berger_clock_microphase_tail_envelope import CERTIFICATE, build


def main() -> int:
    stored = json.loads(CERTIFICATE.read_text())
    if stored != build():
        raise AssertionError("Berger clock-microphase tail-envelope certificate is stale")
    analysis = stored["cutoff_analysis"]
    if analysis["first_sufficient_frozen_profile_retained_max_two_j"] != 3421:
        raise AssertionError("frozen-profile cutoff target drifted")
    if any(row["frozen_profile_tail_below_one"] for row in analysis["current_cutoff_rows"]):
        raise AssertionError("non-small current cutoff was promoted")
    if not all(row["frozen_profile_tail_below_one"] for row in analysis["first_sufficient_rows"]):
        raise AssertionError("sufficient frozen-profile cutoff failed")
    if analysis["moving_profile_status"] != "NO_CERTIFIED_MAP":
        raise AssertionError("moving profile was identified with the frozen-vector theorem")
    flags = stored["flags"]
    if flags["MOVING_DETECTOR_PROFILE_CLOCK_DERIVATIVE_BOUND_EXPORTED"] is not False:
        raise AssertionError("moving-profile derivative gate was promoted")
    if Fraction(stored["clock_envelope"]["normalized_envelope_constant_C_upper"]) <= 0:
        raise AssertionError("invalid clock envelope constant")
    print("Berger clock-microphase tail-envelope verification: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
