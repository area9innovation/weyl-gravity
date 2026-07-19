from closed_universe_observers.generate_berger_recoil_scalar_stream_activation_gate import build


def test_analytic_tail_envelope_and_symbolic_modewise_word_are_ready():
    value = build()
    rows = {row["id"]: row["status"] for row in value["readiness"]["internal_rows"]}
    assert rows["response_specific_stopping_envelope"] == "CERTIFIED"
    assert rows["complete_modewise_recoil_scalar_integrand"] == "CERTIFIED"
    assert value["readiness"]["symbolic_modewise_word_ready"] is True
    assert value["readiness"]["internal_modewise_stream_ready"] is False


def test_preparation_and_advanced_words_are_symbolically_serialized():
    rows = {row["id"]: row["status"] for row in build()["readiness"]["internal_rows"]}
    assert rows["complete_symbolic_harmonic_preparation_functional"] == "CERTIFIED"
    assert rows["advanced_massive_preparation_operator_word"] == "CERTIFIED"


def test_external_parameters_are_deferred_until_executable_backend():
    value = build()
    assert value["sequencing_decision"]["parameterization_during_internal_gate"] == (
        "hold tilde_u_0,tilde_u_1 fixed; m_0,m_1 symbolic positive; factor explicit g_b g_c^2 monomials"
    )
    assert all(row["status"] == "OPEN" for row in value["readiness"]["external_rows"])
    assert all(row["activation"] == "DEFERRED" for row in value["readiness"]["external_rows"])
    assert value["sequencing_decision"]["current_active_gate"] == (
        "bind every two_j=6 feedback channel-column block and certify the complex-channel-to-real-shell scalar map"
    )
    assert value["flags"]["FOUR_RECOIL_SCALAR_STREAM_ACTIVE"] is False


def test_missing_execution_capabilities_obstruct_activation():
    value = build()
    rows = {row["id"]: row["status"] for row in value["readiness"]["internal_rows"]}
    assert rows["finite_detector_coefficient_provider_two_j0_to_4"] == "CERTIFIED"
    assert rows["finite_polynomial_nested_time_convolution"] == "CERTIFIED"
    assert rows["finite_exact_mode_kernel_interval_enclosure"] == "CERTIFIED"
    assert rows["finite_detector_matched_absolute_g3_feedback_channels"] == "CERTIFIED"
    assert rows["finite_partitioned_detector_matched_absolute_g3_feedback"] == "CERTIFIED"
    assert rows["finite_cross_window_detector_advanced_maxwell_remainder"] == "CERTIFIED"
    assert rows["finite_six_mismatched_absolute_g3_feedback_channels"] == "CERTIFIED"
    assert rows["finite_first_omitted_shell_direct_provider_two_j5"] == "CERTIFIED"
    assert rows["finite_two_j5_all_channel_column_feedback_binding"] == "CERTIFIED"
    assert rows["callable_shell_interval_backend"] == "CERTIFIED"
    assert rows["complete_detector_coefficient_provider"] == "CERTIFIED"
    assert rows["nested_time_convolution_backend"] == "OBSTRUCTED"
    assert rows["tail_aware_aggregate_stop_loop"] == "CERTIFIED"
    assert rows["generic_direct_finite_shell_provider"] == "CERTIFIED"
    assert rows["complex_channel_to_real_shell_scalar_map"] == "OBSTRUCTED"
    assert value["atlas_status"] == "OBSTRUCTED"
