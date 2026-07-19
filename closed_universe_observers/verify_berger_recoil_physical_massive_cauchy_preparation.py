#!/usr/bin/env python3
import json
from closed_universe_observers.generate_berger_recoil_physical_massive_cauchy_preparation import CERTIFICATE,build
def main():
 v=json.loads(CERTIFICATE.read_text());assert v==build();assert v["flags"]["EMITTER_FULL_FORM_CAUCHY_PAIR_EXPORTED"];assert not v["flags"]["POSITIVE_ENERGY_DUAL_COEFFICIENTS_EXPORTED"];print("Berger recoil physical massive Cauchy preparation verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
