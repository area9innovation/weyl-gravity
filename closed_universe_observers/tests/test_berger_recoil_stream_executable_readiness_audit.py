from closed_universe_observers.generate_berger_recoil_stream_executable_readiness_audit import build


def test_symbolic_word_is_not_promoted_to_an_interval_backend():
    value = build()
    rows = {row["id"]: row["status"] for row in value["readiness"]["rows"]}
    assert rows["complete_symbolic_operator_word"] == "CERTIFIED"
    assert rows["finite_detector_coefficient_provider_two_j0_to_4"] == "CERTIFIED"
    assert rows["detector_profile_coefficient_provider"] == "CERTIFIED"
    assert rows["finite_polynomial_nested_time_convolution"] == "CERTIFIED"
    assert rows["finite_exact_mode_kernel_interval_enclosure"] == "CERTIFIED"
    assert rows["finite_detector_advanced_maxwell_Dhat1_binding"] == "CERTIFIED"
    assert rows["finite_switched_diagonal_massive_advanced_preparation"] == "CERTIFIED"
    assert rows["finite_physical_massive_advanced_cauchy_pair"] == "CERTIFIED"
    assert rows["finite_coupling_stripped_positive_energy_preparation_coefficients"] == "CERTIFIED"
    assert rows["finite_free_emitter_first_retarded_maxwell_channel"] == "CERTIFIED"
    assert rows["finite_partitioned_detector_selected_leading_response_rank_two"] == "CERTIFIED"
    assert rows["finite_detector_matched_absolute_g3_feedback_channels"] == "CERTIFIED"
    assert rows["finite_partitioned_detector_matched_absolute_g3_feedback"] == "CERTIFIED"
    assert rows["finite_cross_window_detector_advanced_maxwell_remainder"] == "CERTIFIED"
    assert rows["finite_six_mismatched_absolute_g3_feedback_channels"] == "CERTIFIED"
    assert rows["finite_first_omitted_shell_direct_provider_two_j5"] == "CERTIFIED"
    assert rows["finite_two_j5_all_channel_column_feedback_binding"] == "CERTIFIED"
    assert rows["generic_direct_finite_shell_provider"] == "CERTIFIED"
    assert rows["complex_channel_to_real_shell_scalar_map"] == "CERTIFIED"
    assert rows["finite_two_j6_reality_folded_feedback_binding"] == "CERTIFIED"
    assert rows["nested_time_convolution_backend"] == "OBSTRUCTED"
    assert rows["shell_interval_evaluator"] == "CERTIFIED"
    assert rows["tail_aware_aggregate_stop_loop"] == "CERTIFIED"
    assert value["atlas_status"] == "OBSTRUCTED"


def test_external_specialization_is_deferred_until_backend_exists():
    value = build()
    assert value["readiness"]["internal_executable_stream_ready"] is False
    assert value["readiness"]["external_specialization_deferred"] is True
    assert value["flags"]["NUMERICAL_SPECIALIZATION_INPUT_SCHEMA_EXPORTED"] is True
    assert value["flags"]["NUMERICAL_SPECIALIZATION_VALUES_DECLARED"] is False


def test_generic_direct_reality_and_tail_stop_leave_complete_nested_stream_fail_closed():
    rows = build()["readiness"]["rows"][1:]
    assert len(rows) == 22
    assert [row["status"] for row in rows].count("CERTIFIED") == 21
    assert [row["status"] for row in rows].count("OBSTRUCTED") == 1
