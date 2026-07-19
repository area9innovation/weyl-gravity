from closed_universe_observers.generate_berger_108_row_q1_pbw_background_ideal_obstruction import build, free_jet_witness


def test_free_jet_noether_residual_is_exactly_nonzero():
    value = free_jet_witness()
    assert value["free_jet_residual_term_count"] == 4
    assert value["separating_evaluation"] == {"assignment": "R0_1 jet [0,3,0,0]=1 and the other displayed third jets=0", "value": "1", "nonzero": True}


def test_background_equation_requires_differential_prolongation():
    assert "prolongations" in free_jet_witness()["on_shell_differential_ideal_reduction"]


def test_residual_term_deletion_is_detected():
    assert free_jet_witness(delete_one_term=True)["free_jet_residual_term_count"] == 3


def test_existing_covariant_and_on_shell_results_are_preserved():
    value = build()
    assert value["flags"]["COVARIANT_ROD_NOETHER_IDENTITY_PRESERVED"]
    assert value["flags"]["GLOBAL_ROD_ON_SHELL_WAVE_EQUATIONS_PRESERVED"]


def test_scalar_q1_promotion_remains_fail_closed():
    value = build()
    assert value["flags"]["BACKGROUND_DIFFERENTIAL_IDEAL_MISSING"]
    assert not value["flags"]["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
    assert all(row["detected"] for row in value["mutations"])
