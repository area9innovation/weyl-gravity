#!/usr/bin/env python3
import argparse,json
from fractions import Fraction
from closed_universe_observers.generate_berger_adaptive_clock_weighted_scalar_stream import CLOCK_POWERS,build,certificate_path
def main()->int:
 p=argparse.ArgumentParser();p.add_argument("--power",type=int,choices=CLOCK_POWERS,required=True);a=p.parse_args();v=json.loads(certificate_path(a.power).read_text());assert v==build(a.power);assert v["coverage"]=={"mode_count":140,"serialized_unique_diagonal_count":4970,"reconstructed_full_diagonal_count":9870};assert Fraction(v["truncation_remainder_audit"]["maximum_uniform_remainder_upper"])<Fraction(1,10**150);print(f"adaptive S{a.power} verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
