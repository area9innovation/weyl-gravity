import json

from closed_universe_observers.generate_berger_108_row_memory_transport_q3_pbw import (
    CERTIFICATE, PAYLOAD, velocity_second_jet,
)


def documents():
    return json.loads(CERTIFICATE.read_text()), json.loads(PAYLOAD.read_text())


def test_clock_flow_second_jet_is_exact():
    certificate, _ = documents()
    audit = certificate["velocity_and_cyclicity_audit"]
    assert audit["first_jet_recovery_defect_count"] == 0
    assert audit["second_jet_permutation_defect_count"] == 0
    assert audit["direct_directional_second_variation_defect_count"] == 0
    assert velocity_second_jet()


def test_memory_q3_is_symmetric_and_cyclic():
    certificate, _ = documents()
    audit = certificate["velocity_and_cyclicity_audit"]
    assert audit["graded_symmetry_defect_count"] == 0
    assert audit["p_to_m_formal_transpose_defect_count"] == 0
    assert audit["p_to_geometry_formal_transpose_defect_count"] == 0


def test_payload_support_and_fail_closed_boundary():
    certificate, payload = documents()
    assert payload["nonzero_output_rows"] == list(range(27, 37)) + [38] + list(range(80, 84))
    assert payload["operator_key_count"] > 0
    assert payload["serialized_term_count"] >= payload["operator_key_count"]
    disposition = certificate["activation_disposition"]
    assert disposition["memory_transport_q3_subblock_exported"] is True
    assert disposition["complete_scalar_q3_exported"] is False
    assert disposition["arity_replay_certified"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
