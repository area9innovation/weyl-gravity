#!/usr/bin/env python3
import json
from fractions import Fraction
from closed_universe_observers.generate_berger_adaptive_clock_weighted_polarization_stream import CERTIFICATE,POWERS,build
def main()->int:
 v=json.loads(CERTIFICATE.read_text());assert v==build();assert v["coverage"]=={"detector_component_entry_count":86736,"detector_component_scalar_term_application_count":231018,"clock_power_interval_count":780624};assert v["direct_p12_compatibility_audit"]["nonoverlap_defect_count"]==0;assert all(Fraction(x)>0 for x in v["maximum_interval_width_by_clock_power"].values());assert list(map(int,v["maximum_interval_width_by_clock_power"]))==list(POWERS);print("adaptive polarization verification: PASS");return 0
if __name__=="__main__":raise SystemExit(main())
