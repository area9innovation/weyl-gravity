import json
from closed_universe_observers.atlas.generate_observer_atlas_fragment import OBSERVER_FIELDS, OUTPUT, build
from residual_atlas.validate_fragment import validate

def test_generated_fragment_is_current():
    assert json.loads(OUTPUT.read_text()) == build()
    validate(OUTPUT)

def test_operational_fields_and_fail_closed_crosswalk():
    value = build()
    assert all(set(row["observer_data"]) == set(OBSERVER_FIELDS) for row in value["entries"])
    crosswalks = [row for row in value["entries"] if "crosswalk" in row["id"]]
    assert len(crosswalks) == 2
    assert all(set(row["descriptions"].values()) == {"NO_CERTIFIED_MAP"} for row in crosswalks)


def test_berger_physical_branch_bridge_is_inactive():
    row = next(row for row in build()["entries"] if row["id"] == "observer.crosswalk.berger_physical_branch_to_detector")
    assert row["observer_data"]["detector_response"]["status"] == "NO_CERTIFIED_MAP"
    assert row["mode_data"]["second_order"]["causal_retarded"]["status"] == "NO_CERTIFIED_MAP"

def test_tangent_cone_is_not_promoted():
    row = next(row for row in build()["entries"] if row["id"] == "observer.berger.second_order_cone_restriction")
    assert row["observer_data"]["detector_restriction_to_second_order_cone"]["status"] == "OPEN"
    second_order = row["mode_data"]["second_order"]
    assert {second_order[name]["status"] for name in ("bounded_or_finite_quasiperiodic", "smooth_secular", "causal_retarded")} == {"OPEN"}


def test_recoil_executable_readiness_is_fail_closed():
    rows = {row["id"]: row for row in build()["entries"]}
    readiness = rows["observer.berger.detector_profile.recoil_stream_executable_readiness"]
    activation = rows["observer.berger.detector_profile.recoil_scalar_stream_activation"]
    assert readiness["descriptions"]["causal"] == "OBSTRUCTED"
    assert readiness["observer_data"]["detector_response"]["status"] == "OBSTRUCTED"
    assert activation["observer_data"]["profile_green_boundary_dependencies"]["status"] == "OBSTRUCTED"
    assert "BERGER_RECOIL_STREAM_EXECUTABLE_READINESS_AUDIT" in {
        evidence["result_id"] for evidence in activation["evidence"]
    }


def test_partitioned_leading_rank_two_keeps_nonlinear_and_quotient_gates_open():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.recoil_partitioned_leading_response_rank_two"
    )
    assert row["descriptions"]["observational"] == "CERTIFIED"
    assert row["descriptions"]["nonlinear"] == "OPEN"
    assert row["observer_data"]["response_rank"]["status"] == "CERTIFIED"
    assert row["observer_data"]["relational_redshift_contribution"]["status"] == "OPEN"
    assert row["observer_data"]["survives_gauge_reduction"]["status"] == "NO_CERTIFIED_MAP"
    assert row["observer_data"]["detector_restriction_to_second_order_cone"]["status"] == "OPEN"


def test_recoil_shell_aggregation_is_certified_without_physical_response_promotion():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.recoil_finite_shell_interval_aggregator"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"
    assert "BERGER_RECOIL_FINITE_SHELL_INTERVAL_AGGREGATOR" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_finite_detector_provider_is_certified_without_all_shell_promotion():
    rows = {row["id"]: row for row in build()["entries"]}
    finite = rows["observer.berger.detector_profile.recoil_finite_detector_coefficient_provider"]
    readiness = rows["observer.berger.detector_profile.recoil_stream_executable_readiness"]
    assert finite["descriptions"]["causal"] == "CERTIFIED"
    assert finite["observer_data"]["detector_response"]["status"] == "OPEN"
    assert finite["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"
    assert readiness["observer_data"]["detector_response"]["status"] == "OBSTRUCTED"
    assert "BERGER_RECOIL_FINITE_DETECTOR_COEFFICIENT_PROVIDER" in {
        evidence["result_id"] for evidence in finite["evidence"]
    }


def test_finite_nested_convolution_is_certified_without_physical_binding():
    rows = {row["id"]: row for row in build()["entries"]}
    finite = rows["observer.berger.detector_profile.recoil_finite_nested_time_convolution"]
    readiness = rows["observer.berger.detector_profile.recoil_stream_executable_readiness"]
    assert finite["descriptions"]["causal"] == "CERTIFIED"
    assert finite["observer_data"]["detector_response"]["status"] == "OPEN"
    assert finite["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"
    assert readiness["observer_data"]["detector_response"]["status"] == "OBSTRUCTED"


def test_exact_mode_kernel_payload_is_certified_without_interval_promotion():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.recoil_exact_mode_kernel_payload"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"


def test_mixed_unary_precedes_apparatus_and_affine_k_morphism():
    value = build()
    row = next(row for row in value["entries"] if row["id"] == "observer.berger.massive_emitter.preparation_pair")
    result_ids = [evidence["result_id"] for evidence in row["evidence"]]
    assert result_ids.index("BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY") < result_ids.index("BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE")
    assert result_ids.index("BERGER_84_ROW_APPARATUS_Q2_Q3_K_GATE") < result_ids.index("BERGER_AFFINE_K_OBSERVER_MORPHISM")


def test_adaptive_row_imports_polarization_stream_without_green_promotion():
    row = next(row for row in build()["entries"] if row["id"] == "observer.berger.detector_profile.adaptive_cutoff_preflight")
    assert "BERGER_CLOCK_WEIGHTED_POLARIZATION_STREAM_TWO_J138" in {
        evidence["result_id"] for evidence in row["evidence"]
    }
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"


def test_selected_clock_power_row_is_input_certified_and_response_open():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.selected_clock_power_polarized_form"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["clock_and_rod_dependence"]["status"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["response_rank"]["status"] == "OPEN"
    assert "BERGER_SELECTED_CLOCK_POWER_POLARIZED_FORM_RAIL" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_selected_charge_block_promotion_is_fail_closed():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.selected_charge_block_companion_closure"
    )
    assert row["descriptions"]["causal"] == "OBSTRUCTED"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "OBSTRUCTED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert "BERGER_SELECTED_CHARGE_BLOCK_COMPANION_CLOSURE_GATE" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_selected_scalar_companion_completion_does_not_promote_form_response():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.selected_charge_block_scalar_companion_completion"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert "BERGER_SELECTED_CHARGE_BLOCK_SCALAR_COMPANION_COMPLETION" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_selected_form_companion_clock_rail_closes_inputs_not_response():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.selected_charge_block_form_companion_clock_rail"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["response_rank"]["status"] == "OPEN"
    assert "BERGER_SELECTED_CHARGE_BLOCK_FORM_COMPANION_CLOCK_RAIL" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_selected_temporal_bandwidth_preflight_is_fail_closed():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.selected_charge_block_temporal_bandwidth_preflight"
    )
    assert row["descriptions"]["causal"] == "OBSTRUCTED"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "OBSTRUCTED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["response_rank"]["status"] == "OPEN"
    assert "BERGER_SELECTED_CHARGE_BLOCK_TEMPORAL_BANDWIDTH_PREFLIGHT" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_selected_correlated_clock_transform_certifies_image_not_response():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.selected_charge_block_correlated_clock_transform"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["response_rank"]["status"] == "OPEN"
    assert "BERGER_SELECTED_CHARGE_BLOCK_CORRELATED_CLOCK_TRANSFORM" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_green_weighted_tail_reduction_is_certified_without_tail_promotion():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.green_weighted_spatial_tail_reduction"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["survives_gauge_reduction"]["status"] == "OPEN"
    assert "BERGER_GREEN_WEIGHTED_SPATIAL_TAIL_REDUCTION" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_haar_normalization_repair_supersedes_capacity_label_fail_closed():
    rows = {row["id"]: row for row in build()["entries"]}
    repair = rows["observer.berger.detector_profile.haar_normalization_repair"]
    adaptive = rows["observer.berger.detector_profile.adaptive_cutoff_preflight"]
    assert repair["descriptions"]["causal"] == "CERTIFIED"
    assert repair["observer_data"]["detector_response"]["status"] == "OPEN"
    assert "two_j=97" in repair["observer_data"]["profile_green_boundary_dependencies"]["statement"]
    assert "two_j=138" in adaptive["scope"]["ell"]
    assert "working rail" in adaptive["scope"]["ell"]
    assert "BERGER_HAAR_PROFILE_NORMALIZATION_REPAIR" in {
        evidence["result_id"] for evidence in repair["evidence"]
    }


def test_clock_uniform_sobolev_n1_exports_finite_tail_without_full_image():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.clock_uniform_sobolev_n1"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["profile_green_boundary_dependencies"]["status"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["survives_gauge_reduction"]["status"] == "OPEN"
    assert "does not certify smallness" in row["observer_data"]["profile_green_boundary_dependencies"]["statement"]
    assert "BERGER_CLOCK_UNIFORM_PROFILE_SOBOLEV_N1" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_correlated_sobolev_n1_improves_bound_without_small_tail_promotion():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.correlated_sobolev_n1"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "OPEN"
    assert row["observer_data"]["survives_gauge_reduction"]["status"] == "OPEN"
    statement = row["observer_data"]["profile_green_boundary_dependencies"]["statement"]
    assert "below 1.95e3" in statement
    assert "nor obstructs the true tail" in statement
    assert "BERGER_CORRELATED_PROFILE_SOBOLEV_N1" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_matched_absolute_g3_feedback_is_evaluated_without_rank_promotion():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.recoil_matched_absolute_g3_feedback_channels"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["descriptions"]["observational"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "CERTIFIED"
    assert row["observer_data"]["response_rank"]["status"] == "OPEN"
    assert row["observer_data"]["recoil_backreaction_order"]["status"] == "CERTIFIED"
    assert row["observer_data"]["survives_gauge_reduction"]["status"] == "NO_CERTIFIED_MAP"
    assert row["observer_data"]["detector_restriction_to_second_order_cone"]["status"] == "OPEN"
    assert "both contain zero" in row["observer_data"]["detector_response"]["statement"]
    assert "BERGER_RECOIL_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_partitioned_matched_feedback_records_contraction_without_nonzero_promotion():
    row = next(
        row for row in build()["entries"]
        if row["id"] == "observer.berger.detector_profile.recoil_partitioned_matched_absolute_g3_feedback"
    )
    assert row["descriptions"]["causal"] == "CERTIFIED"
    assert row["observer_data"]["detector_response"]["status"] == "CERTIFIED"
    assert row["observer_data"]["response_rank"]["status"] == "OPEN"
    assert row["observer_data"]["survives_gauge_reduction"]["status"] == "NO_CERTIFIED_MAP"
    statement = row["observer_data"]["detector_response"]["statement"]
    assert "contract strictly from 2 to 4 to 8 cells" in statement
    assert "both 8-cell intervals contain zero" in statement
    assert "BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK" in {
        evidence["result_id"] for evidence in row["evidence"]
    }


def test_six_mismatched_feedback_channels_record_four_zeros_and_two_open_signs():
    rows = {row["id"]: row for row in build()["entries"]}
    cross = rows[
        "observer.berger.detector_profile.recoil_cross_window_detector_advanced_maxwell_remainder"
    ]
    mismatch = rows[
        "observer.berger.detector_profile.recoil_six_mismatched_absolute_g3_feedback_channels"
    ]
    assert cross["observer_data"]["detector_response"]["status"] == "OPEN"
    assert cross["observer_data"]["clock_and_rod_dependence"]["status"] == "CERTIFIED"
    assert mismatch["observer_data"]["detector_response"]["status"] == "CERTIFIED"
    assert mismatch["observer_data"]["response_rank"]["status"] == "OPEN"
    assert mismatch["observer_data"]["survives_gauge_reduction"]["status"] == "NO_CERTIFIED_MAP"
    statement = mismatch["observer_data"]["detector_response"]["statement"]
    assert "I_001, I_010, I_011 and I_110 are exact support zeros" in statement
    assert "I_100 and I_101" in statement
    assert "BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS" in {
        evidence["result_id"] for evidence in mismatch["evidence"]
    }
