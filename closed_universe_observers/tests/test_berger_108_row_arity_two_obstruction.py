import json

from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import CERTIFICATE


def document():
    return json.loads(CERTIFICATE.read_text())


def test_typed_base_is_zero_but_complete_degree_zero_is_obstructed():
    audit = document()["arity_two_replay"]
    assert audit["typed_64_row_base_control_summary"]["operator_key_count"] == 0
    assert audit["complete_defect_summary"]["operator_key_count"] == 4408
    assert audit["complete_defect_summary"]["serialized_term_count"] == 4732


def test_first_witness_is_exact_and_survives_background_quotient():
    audit = document()["arity_two_replay"]
    witness = audit["first_lexicographic_defect"]
    assert (witness["output_row"], witness["left_input_row"], witness["right_input_row"]) == (49, 3, 74)
    assert witness["coefficient"][0]["coefficient"]["rational"] == {"numerator": 1, "denominator": 1}
    assert len(witness["background_quotient_nonzero_modes"]) == 2
    assert set(audit["first_defect_q2_source_isolation"]) == {"base_gravity_clock"}
    assert set(audit["first_defect_q1_source_isolation"]) == {"local_rod"}


def test_obstruction_keeps_every_downstream_gate_closed():
    value = document()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["activation_disposition"]["arity_three_replay_authorized"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
    assert value["flags"]["COMPONENT_ARITY_IDENTITIES_CERTIFIED"] is False
