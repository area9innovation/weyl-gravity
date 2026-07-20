import json

from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import CERTIFICATE


def document():
    return json.loads(CERTIFICATE.read_text())


def test_typed_base_is_zero_but_complete_degree_zero_is_obstructed():
    audit = document()["arity_two_replay"]
    assert audit["typed_64_row_base_control_summary"]["operator_key_count"] == 0
    assert audit["formal_differential_coefficient_defect_summary"]["operator_key_count"] == 3984
    assert audit["complete_defect_summary"]["operator_key_count"] == 2772
    assert audit["complete_defect_summary"]["serialized_term_count"] == 2820


def test_first_same_background_witness_is_exact_after_switch_quotient():
    audit = document()["arity_two_replay"]
    witness = audit["first_lexicographic_defect"]
    assert (witness["output_row"], witness["left_input_row"], witness["right_input_row"]) == (49, 55, 84)
    assert witness["left_pbw_multiindex"] == [0, 1, 0, 0]
    assert witness["right_pbw_multiindex"] == [0, 1, 0, 0]
    assert witness["coefficient"][0]["coefficient"]["rational"] == {"numerator": -3, "denominator": 1}
    assert witness["background_quotient_evaluation_status"] == "NOT_APPLICABLE_FORMAL_PARAMETER_PROFILE_COEFFICIENT"
    assert witness["background_quotient_nonzero_modes"] == []
    assert audit["emitter_switch_specialization"]["clock_rate_e0_Theta_bar"] == "3/4"
    assert set(audit["first_defect_q2_source_isolation"]) == {"base_maxwell_typed", "emitter_physical"}
    assert set(audit["first_defect_q1_source_isolation"]) == {"base_gravity_clock_maxwell", "emitter"}


def test_obstruction_keeps_every_downstream_gate_closed():
    value = document()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["activation_disposition"]["arity_three_replay_authorized"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
    assert value["flags"]["COMPONENT_ARITY_IDENTITIES_CERTIFIED"] is False
