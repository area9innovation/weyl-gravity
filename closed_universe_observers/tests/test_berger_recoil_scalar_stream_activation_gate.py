from closed_universe_observers.generate_berger_recoil_scalar_stream_activation_gate import build


def test_analytic_tail_envelope_and_symbolic_modewise_integrand_are_ready():
    value = build()
    rows = {row["id"]: row["status"] for row in value["readiness"]["internal_rows"]}
    assert rows["response_specific_stopping_envelope"] == "CERTIFIED"
    assert rows["complete_modewise_recoil_scalar_integrand"] == "CERTIFIED"
    assert value["readiness"]["internal_modewise_stream_ready"] is True


def test_preparation_and_advanced_words_are_symbolically_serialized():
    rows = {row["id"]: row["status"] for row in build()["readiness"]["internal_rows"]}
    assert rows["complete_symbolic_harmonic_preparation_functional"] == "CERTIFIED"
    assert rows["advanced_massive_preparation_operator_word"] == "CERTIFIED"


def test_external_parameters_are_a_later_separate_gate():
    value = build()
    assert value["sequencing_decision"]["parameterization_during_internal_gate"] == (
        "hold tilde_u_0,tilde_u_1 fixed; m_0,m_1 symbolic positive; factor explicit g_b g_c^2 monomials"
    )
    assert all(row["status"] == "OPEN" for row in value["readiness"]["external_rows"])
    assert value["flags"]["FOUR_RECOIL_SCALAR_STREAM_ACTIVE"] is False
