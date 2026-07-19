import json

from closed_universe_observers.generate_berger_108_row_q3_structural_zero_ledger import CERTIFICATE


def document():
    return json.loads(CERTIFICATE.read_text())


def test_bv_sources_are_exact_cubic_actions():
    value = document()
    audits = {item["source"]: item for item in value["source_audits"]}
    assert audits["apparatus_scalar_BV"]["q2_serialized_term_count"] == 240
    assert audits["emitter_Diff_BV"]["q2_serialized_term_count"] == 912
    for audit in audits.values():
        assert audit["pairing_lowering_defect_count"] == 0
        assert audit["nonconstant_coefficient_factor_count"] == 0
        assert audit["exact_action_field_degree"] == 3
        assert audit["fourth_frechet_derivative_term_count"] == 0
        assert audit["q3_operator_key_count"] == 0
        assert audit["structural_zero_certified"] is True


def test_zero_payload_and_downstream_gates_are_fail_closed():
    value = document()
    assert value["empty_q3_payload"]["shape"] == [108, 108, 108, 108]
    assert value["empty_q3_payload"]["rows"] == []
    assert value["mutation_results"][0]["detected"] is True
    disposition = value["activation_disposition"]
    assert disposition["structural_q3_zero_ledger_complete"] is True
    assert disposition["complete_scalar_q3_exported"] is False
    assert disposition["arity_replay_certified"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
