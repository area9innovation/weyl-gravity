from closed_universe_observers.generate_berger_per_shell_recoil_operator_word import (
    _composition_defects,
    block_audit,
    build,
    recoil_operations,
)


def test_preparation_and_recoil_words_compose_on_nontrivial_shell():
    row = block_audit(3)
    assert row["preparation_composition_defect_count"] == 0
    assert row["recoil_composition_defect_count"] == 0
    assert row["space_dimensions"]["maxwell_one_form"] == 16
    assert row["space_dimensions"]["emitter_two_form"] == 24


def test_wrong_feedback_derivative_is_type_rejected():
    wrong = recoil_operations(2, swap_feedback_d_for_delta=True)
    assert _composition_defects(wrong) > 0


def test_all_eight_channels_and_four_aggregate_streams_are_serialized():
    value = build()
    assert len(value["channel_integrands"]) == 8
    assert len(value["aggregate_streams"]) == 4
    assert {row["absolute_g3_monomial"] for row in value["channel_integrands"]} == {
        "g_0 g_0^2",
        "g_0 g_1^2",
        "g_1 g_0^2",
        "g_1 g_1^2",
    }
    assert value["channel_integrands"][1]["bare_tail_radius"] == "D_0 C_1(m_1) E_A,0"


def test_symbolic_integrand_does_not_activate_numerical_streams():
    value = build()
    assert value["flags"]["COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED"] is True
    assert value["external_specialization_gate"]["four_streams_active"] is False
