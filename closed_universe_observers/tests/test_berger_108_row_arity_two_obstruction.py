from closed_universe_observers.generate_berger_108_row_arity_two_obstruction import (
    build,
    replay_audit,
)


def test_typed_base_is_zero_but_complete_degree_zero_is_obstructed():
    audit = replay_audit()
    assert audit["typed_64_row_base_control_summary"]["operator_key_count"] == 0
    assert audit["complete_defect_summary"]["operator_key_count"] == 4768
    assert audit["complete_defect_summary"]["serialized_term_count"] == 5128


def test_first_witness_is_exact_and_survives_background_quotient():
    witness = replay_audit()["first_lexicographic_defect"]
    assert (witness["output_row"], witness["left_input_row"], witness["right_input_row"]) == (49, 0, 74)
    assert witness["coefficient"][0]["coefficient"]["rational"] == {"numerator": -1, "denominator": 1}
    assert len(witness["background_quotient_nonzero_modes"]) == 2
    assert set(replay_audit()["first_defect_source_isolation"]) == {"apparatus_scalar_BV"}


def test_obstruction_keeps_every_downstream_gate_closed():
    value = build()
    assert value["atlas_status"] == "OBSTRUCTED"
    assert value["activation_disposition"]["arity_three_replay_authorized"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
    assert value["flags"]["COMPONENT_ARITY_IDENTITIES_CERTIFIED"] is False
