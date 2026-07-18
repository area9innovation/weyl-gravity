#!/usr/bin/env python3
import json
from fractions import Fraction
from closed_universe_observers.generate_berger_moving_profile_clock_derivative_tail import CERTIFICATE, build

def main():
    value=json.loads(CERTIFICATE.read_text())
    assert value==build()
    assert value["flags"]["MOVING_DETECTOR_PROFILE_CLOCK_DERIVATIVE_BOUND_EXPORTED"] is True
    assert value["flags"]["COMPLETE_LOW_MODE_PROJECTION_EXPORTED"] is False
    cutoff=value["calculation"]["first_sufficient_moving_profile_retained_max_two_j"]
    assert all(Fraction(v)<1 for v in value["calculation"]["sufficient_cutoff_tail_uppers"].values())
    assert not all(Fraction(v)<1 for v in value["calculation"]["previous_cutoff_tail_uppers"].values())
    print("Berger moving-profile clock-derivative tail verification: PASS")
    return 0

if __name__=="__main__": raise SystemExit(main())
