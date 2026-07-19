import json

from closed_universe_observers.generate_berger_108_row_complete_q3_pbw import CERTIFICATE, PAYLOAD


def documents():
    return json.loads(CERTIFICATE.read_text()), json.loads(PAYLOAD.read_text())


def test_complete_q3_has_all_sources_without_key_collisions():
    certificate, payload = documents()
    assert payload["source_term_counts"] == {
        "base_gravity_clock_maxwell": 59598,
        "rod_metric": 181344,
        "memory_transport": 5196,
        "normalized_readout": 1085112,
        "emitter_physical": 107988,
        "structural_zeros": 0,
    }
    assert payload["operator_key_count"] == 616738
    assert payload["serialized_term_count"] == 1439238
    assert payload["cross_source_operator_key_collision_count"] == 0
    assert len(payload["chunks"]) == 43
    assert all(item["detected"] for item in certificate["assembly_audit"]["source_deletion_mutations"].values())


def test_complete_q3_exports_only_the_payload_gate():
    certificate, payload = documents()
    assert payload["nonzero_output_rows"] == list(range(27, 39)) + list(range(49, 53)) + [54] + list(range(59, 63)) + list(range(74, 84)) + list(range(96, 108))
    disposition = certificate["activation_disposition"]
    assert disposition["complete_scalar_q3_payload_assembled"] is True
    assert disposition["structural_q3_zero_ledger_complete"] is True
    assert disposition["arity_replay_certified"] is False
    assert disposition["K_Berger_equivariance_certified"] is False
    assert disposition["observer_morphism_stability_certified"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
