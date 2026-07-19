import json

from closed_universe_observers.generate_berger_108_row_emitter_physical_q3_pbw import CERTIFICATE, PAYLOAD


def documents():
    return json.loads(CERTIFICATE.read_text()), json.loads(PAYLOAD.read_text())


def test_emitter_second_jet_regresses_q2_and_direct_fixtures():
    certificate, _ = documents()
    audit = certificate["second_jet_and_cyclicity_audit"]
    assert audit["q2_cubic_action_regression_key_count"] == 768
    assert audit["q2_cubic_action_regression_defect_count"] == 0
    assert audit["first_metric_jet_component_comparison_count"] == 520
    assert audit["first_metric_jet_component_defect_count"] == 0
    assert audit["second_metric_jet_permutation_defect_count"] == 0
    assert audit["direct_mixed_second_variation_fixture_count"] == 6
    assert audit["direct_mixed_second_variation_defect_count"] == 0
    assert audit["clock_switch_second_derivative_families"] == ["h0_double_prime", "h1_double_prime"]


def test_emitter_q3_support_is_symmetric_and_fail_closed():
    certificate, payload = documents()
    assert payload["operator_key_count"] == 106620
    assert payload["serialized_term_count"] == 107988
    assert payload["nonzero_output_rows"] == list(range(27, 37)) + [38] + list(range(59, 63)) + list(range(96, 108))
    assert certificate["second_jet_and_cyclicity_audit"]["graded_symmetry_defect_count"] == 0
    disposition = certificate["activation_disposition"]
    assert disposition["emitter_physical_q3_subblock_exported"] is True
    assert disposition["complete_scalar_q3_exported"] is False
    assert disposition["structural_q3_zero_ledger_complete"] is False
    assert disposition["arity_replay_certified"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
