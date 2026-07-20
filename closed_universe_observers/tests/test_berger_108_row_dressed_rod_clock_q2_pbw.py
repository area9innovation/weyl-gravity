from closed_universe_observers.generate_berger_108_row_dressed_rod_clock_q2_pbw import (
    build,
    payload_document,
    unary_conjugation_audit,
)


def test_clock_dressing_conjugates_raw_temporal_unary_to_certified_q1():
    audit = unary_conjugation_audit()
    assert audit["unary_conjugation_defect_summary"]["operator_key_count"] == 0
    assert audit["left_inverse_defect_summary"]["operator_key_count"] == 0
    assert audit["right_inverse_defect_summary"]["operator_key_count"] == 0


def test_dressed_rod_clock_q2_payload_has_exact_support():
    payload = payload_document()
    assert payload["operator_key_count"] == 192
    assert payload["serialized_term_count"] == 192
    assert payload["maximum_total_input_order"] == 1


def test_dressed_rod_repair_keeps_downstream_gates_closed():
    value = build()
    assert value["activation_disposition"]["complete_arity_two_identity"] == "OBSTRUCTED_BY_SEPARATE_EMITTER_ORBIT"
    assert value["activation_disposition"]["arity_three_replay_authorized"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
