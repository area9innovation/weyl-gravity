#!/usr/bin/env python3
from __future__ import annotations
from fractions import Fraction
import json
from closed_universe_observers.generate_berger_response_specific_streaming_preflight import CERTIFICATE, build

def main() -> int:
    value=json.loads(CERTIFICATE.read_text())
    assert value==build()
    unit=value["tolerance_capacity_rows"][0]
    assert unit["first_sufficient_retained_max_two_j"]==3835
    assert unit["capacity"]["supported_detector_coordinate_entries"]==44140852
    assert unit["capacity"]["scalar_recurrence_term_applications"]==117703824
    assert unit["capacity"]["legacy_p0_to_p28_clock_power_intervals"]==662112780
    assert value["route_decision"]["maxwell_tail_to_recoil_scalar_map"]=="NO_CERTIFIED_MAP"
    assert all(row["detected"] for row in value["mutation_results"])
    print("Berger response-specific streaming preflight verification: PASS")
    return 0

if __name__=="__main__": raise SystemExit(main())
