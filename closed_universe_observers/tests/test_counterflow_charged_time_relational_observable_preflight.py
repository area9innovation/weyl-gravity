from closed_universe_observers.generate_counterflow_charged_time_relational_observable_preflight import build, exact_algebra, monotonicity, phase_origin_audit


def test_charged_global_covariance():
    a = exact_algebra(); assert a["bracket_psi_Q"] == "1"; assert a["R_label_covariance_defect"] == "0"; assert a["D_label_covariance_defect"] == "0"
    assert exact_algebra(keep_label_fixed=True)["R_label_covariance_defect"] != "0"


def test_clock_and_origin_conditions():
    assert monotonicity()["selected_monotone"]; assert not monotonicity(reverse_charge=True)["selected_monotone"]
    assert phase_origin_audit()["origin_independent"]; assert not phase_origin_audit(endpoint_dependent_shift=True)["origin_independent"]


def test_scope_fails_closed():
    v = build(); assert v["flags"]["CHARGED_TIME_EVENT_MAP_CONTRACT_CERTIFIED"]
    assert v["physical_instantiation_gate"]["status"] == "NO_CERTIFIED_MAP"
    assert not v["flags"]["PHYSICAL_REDSHIFT_CERTIFIED"]; assert not v["flags"]["DETECTOR_RANK_CERTIFIED"]; assert not v["flags"]["QUANTUM_CLAIM"]
