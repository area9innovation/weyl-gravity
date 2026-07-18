#!/usr/bin/env python3
import json
from fractions import Fraction
from closed_universe_observers.generate_berger_high_clock_power_moment_rail import CERTIFICATE,build
def main()->int:
 v=json.loads(CERTIFICATE.read_text());assert v==build();assert [r["k"] for r in v["normalized_clock_even_moments"]]==list(range(15));assert all(Fraction(r["normalized_even_moment"]["width"])<Fraction(1,1000) for r in v["normalized_clock_even_moments"]);print("BERGER_HIGH_CLOCK_POWER_MOMENT_RAIL_P28 verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
