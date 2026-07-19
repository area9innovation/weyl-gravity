from closed_universe_observers.generate_berger_108_row_background_specialization_differential_ideal import (
    build,
)


def test_all_six_rods_and_ten_phi2_components_are_specialized():
    value = build()
    specialization = value["background_specialization"]
    assert specialization["rod_background_count"] == 6
    assert specialization["Phi2_background_count"] == 10
    assert len(specialization["records"]) == 16


def test_target_is_a_berger_differential_algebra():
    value = build()
    audit = value["target_differential_algebra"]
    assert audit["sphere_relation_derivative_defect_count"] == 0
    assert audit["coordinate_commutator_defect_count"] == 0
    assert value["exact_checks"]["background_commutator_defect_count"] == 0


def test_shifted_background_equations_vanish():
    equations = build()["shifted_background_equations"]
    assert equations["rod_wave_residual_nonzero_count"] == 0
    assert equations["metric_zero_mode_residual_nonzero_count"] == 0
    assert equations["metric_positive_mode_residual_nonzero_count"] == 0


def test_former_free_jet_obstruction_dies_only_in_the_quotient():
    value = build()
    checks = value["exact_checks"]
    assert checks["former_free_residual_term_count"] == 4
    assert checks["former_free_residual_quotient_term_count"] == 0
    assert value["differential_ideal"]["e1_Box_R0_1_quotient_normal_form"] == []


def test_q1_payload_remains_fail_closed():
    value = build()
    assert value["flags"]["FREE_JET_Q1_OBSTRUCTION_RESOLVED_IN_QUOTIENT"]
    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    assert all(row["detected"] for row in value["mutations"])
