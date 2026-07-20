import json

from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import CERTIFICATE


def document():
    return json.loads(CERTIFICATE.read_text())


def test_typed_base_is_zero_but_complete_degree_zero_is_obstructed():
    audit = document()["arity_two_replay"]
    assert audit["typed_64_row_base_control_summary"]["operator_key_count"] == 0
    assert audit["formal_differential_coefficient_defect_summary"]["operator_key_count"] == 3432
    assert audit["complete_defect_summary"]["operator_key_count"] == 2340
    assert audit["complete_defect_summary"]["serialized_term_count"] == 2388


def test_first_same_background_witness_is_exact_after_switch_quotient():
    audit = document()["arity_two_replay"]
    witness = audit["first_lexicographic_defect"]
    assert (witness["output_row"], witness["left_input_row"], witness["right_input_row"]) == (52, 55, 84)
    assert witness["left_pbw_multiindex"] == [1, 1, 0, 0]
    assert witness["right_pbw_multiindex"] == [0, 0, 0, 0]
    assert witness["coefficient"][0]["coefficient"]["rational"] == {"numerator": 1, "denominator": 1}
    assert witness["background_quotient_evaluation_status"] == "NOT_APPLICABLE_FORMAL_PARAMETER_PROFILE_COEFFICIENT"
    assert witness["background_quotient_nonzero_modes"] == []
    assert audit["emitter_switch_specialization"]["clock_rate_e0_Theta_bar"] == "3/4"
    assert set(audit["first_defect_q2_source_isolation"]) == {"emitter_Diff_BV"}
    assert set(audit["first_defect_q1_source_isolation"]) == {"emitter"}


def test_obstruction_keeps_every_downstream_gate_closed():
    value = document()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["activation_disposition"]["arity_three_replay_authorized"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
    assert value["flags"]["COMPONENT_ARITY_IDENTITIES_CERTIFIED"] is False


def test_form_clock_chart_is_canonical_but_cannot_repair_the_raw_defect():
    gate = document()["form_clock_chart_gate"]
    assert gate["quadratic_chart_summaries"]["complete"]["operator_key_count"] == 248
    assert gate["conjugation_correction_summaries"]["0,0"]["operator_key_count"] == 3108
    assert all(
        summary["operator_key_count"] == 0
        for summary in gate["correction_arity_two_residuals"].values()
    )
    assert gate["existing_obstruction_change_summary"]["operator_key_count"] == 0
    assert gate["disposition"] == "CERTIFIED_CANONICAL_CHART_CHANGE_DOES_NOT_REPAIR_RAW_WARD_DEFECT"
