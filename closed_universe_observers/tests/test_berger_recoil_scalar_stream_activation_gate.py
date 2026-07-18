from closed_universe_observers.generate_berger_recoil_scalar_stream_activation_gate import build


def test_analytic_tail_envelope_is_ready_but_modewise_integrand_is_not():
    value = build()
    rows = {row["id"]: row["status"] for row in value["readiness"]["internal_rows"]}
    assert rows["response_specific_stopping_envelope"] == "CERTIFIED"
    assert rows["complete_modewise_recoil_scalar_integrand"] == "OPEN"


def test_operator_defined_preparations_are_not_promoted_to_harmonic_data():
    rows = {row["id"]: row["status"] for row in build()["readiness"]["internal_rows"]}
    assert rows["complete_harmonic_preparation_coefficients"] == "OPEN"
    assert rows["advanced_massive_preparation_image"] == "OPEN"


def test_external_parameters_are_a_later_separate_gate():
    value = build()
    assert value["sequencing_decision"]["parameterization_during_internal_gate"] == (
        "hold tilde_u_0,tilde_u_1 fixed; m_0,m_1 symbolic positive; factor explicit g_b g_c^2 monomials"
    )
    assert all(row["status"] == "OPEN" for row in value["readiness"]["external_rows"])
    assert value["flags"]["FOUR_RECOIL_SCALAR_STREAM_ACTIVE"] is False
