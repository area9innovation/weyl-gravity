from closed_universe_observers.generate_berger_response_specific_streaming_preflight import _capacity, build

def test_capacity_formula_matches_certified_two_j138_audit():
    assert _capacity(138)["supported_detector_coordinate_entries"]==57824
    assert _capacity(138)["scalar_recurrence_term_applications"]==154012

def test_unit_tail_target_has_exact_materialization_cost():
    row=build()["tolerance_capacity_rows"][0]
    assert row["first_sufficient_retained_max_two_j"]==3835
    assert row["capacity"]["legacy_p0_to_p28_clock_power_intervals"]==662112780

def test_streaming_route_is_fail_closed_without_chain_dual_norm():
    value=build()
    assert value["route_decision"]["stream_exact_charge_blocks_into_fixed_scalar_functionals"]=="ACTIVE"
    assert value["route_decision"]["maxwell_tail_to_recoil_scalar_map"]=="NO_CERTIFIED_MAP"
    assert value["flags"]["FIXED_MASSIVE_CHAIN_DUAL_NORMS_EXPORTED"] is False
    assert value["flags"]["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False
