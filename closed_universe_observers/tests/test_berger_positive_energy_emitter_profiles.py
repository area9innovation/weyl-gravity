from closed_universe_observers.generate_berger_positive_energy_emitter_profiles import build, energy_dual_audit, support_audit

def test_positive_energy_dual_is_strict() -> None:
    a=energy_dual_audit(); assert a["omega_times_dual"]==[["lambda + m2","0"],["0","1"]]; assert a["strictly_positive_for_nonzero_covector_data"] is True

def test_dual_mutations_fail() -> None:
    assert energy_dual_audit(flip_dual_sign=True)["strictly_positive_for_nonzero_covector_data"] is False
    assert energy_dual_audit(delete_configuration_term=True)["strictly_positive_for_nonzero_covector_data"] is False

def test_slices_have_exact_pre_switch_gap() -> None:
    a=support_audit(); assert a["all_slice_gap_defects_zero"] is True; assert [x["gap"] for x in a["profiles"]]==["1/48","1/48"]

def test_constraints_and_support_are_preserved() -> None:
    assert support_audit()["compact_and_constraint_compatible"] is True

def test_harmonic_evaluation_remains_open() -> None:
    f=build()["flags"]; assert f["OPERATOR_DEFINED_DETECTOR_SELECTED_COMPACT_CAUCHY_PROFILES_EXPORTED"] is True; assert f["HARMONIC_COEFFICIENTS_EVALUATED"] is False; assert f["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"] is False; assert f["QUANTUM_CLAIM"] is False
