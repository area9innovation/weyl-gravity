from closed_universe_observers.generate_berger_108_row_complete_q2_pbw import (
    SOURCES,
    build,
    payload_document,
)


def test_complete_q2_source_counts_and_explicit_additive_overlaps():
    value = payload_document()
    assert SOURCES["base_gravity_clock"].name == "BERGER_SUPPORT_LOCAL_Q2_PAYLOAD.json"
    assert SOURCES["base_maxwell_typed"].name == "BERGER_SUPPORT_LOCAL_COUPLED_MAXWELL_Q2_TYPED_PAYLOAD.json"
    assert value["source_term_counts"] == {
        "base_gravity_clock": 150305,
        "base_maxwell_typed": 1890,
        "apparatus_scalar_BV": 240,
        "dressed_rod_clock": 192,
        "rod_metric": 15852,
        "memory_transport": 192,
        "normalized_readout": 11012,
        "emitter_physical": 6340,
        "emitter_Diff_BV": 912,
    }
    assert value["assembly_audit"]["operator_key_count"] == 171759
    assert value["assembly_audit"]["serialized_term_count"] == 186935
    assert value["assembly_audit"]["cross_source_operator_key_collision_count"] == 160
    assert {tuple(item["sources"]) for item in value["assembly_audit"]["cross_source_operator_key_collisions"]} == {("base_gravity_clock", "rod_metric")}


def test_every_source_deletion_changes_assembly():
    audits = build()["assembly_audit"]["source_deletion_mutations"]
    assert set(audits) == set(SOURCES)
    assert all(item["detected"] for item in audits.values())


def test_complete_q2_does_not_promote_q3_or_cone():
    value = build()
    assert value["activation_disposition"]["complete_scalar_q2_payload_assembled"] is True
    assert value["activation_disposition"]["scalar_q3_exported"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False


def test_complete_q2_requires_typed_base_coderivation_gate():
    value = build()
    assert "base_gravity_q2" in value["gate_refs"]
    assert "base_typed_q2_q3" in value["gate_refs"]
    assert value["flags"]["Q2_ADDITIVE_OVERLAPS_EXPLICIT"] is True
    assert value["flags"]["Q2_CROSS_SOURCE_OPERATOR_KEYS_DISJOINT"] is False
