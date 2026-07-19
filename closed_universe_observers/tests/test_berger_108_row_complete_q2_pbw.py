from closed_universe_observers.generate_berger_108_row_complete_q2_pbw import (
    SOURCES,
    assemble,
    build,
    payload_document,
)


def test_complete_q2_source_counts_and_disjoint_keys():
    value = payload_document()
    assert value["source_term_counts"] == {
        "base_gravity_clock_maxwell": 1890,
        "apparatus_scalar_BV": 240,
        "rod_metric": 15852,
        "memory_transport": 192,
        "normalized_readout": 11012,
        "emitter_physical": 6340,
        "emitter_Diff_BV": 912,
    }
    assert value["assembly_audit"]["operator_key_count"] == 21422
    assert value["assembly_audit"]["serialized_term_count"] == 36438
    assert value["assembly_audit"]["cross_source_operator_key_collision_count"] == 0


def test_every_source_deletion_changes_assembly():
    total = payload_document()["assembly_audit"]["serialized_term_count"]
    assert all(assemble(omit_source=source)[2]["serialized_term_count"] < total for source in SOURCES)


def test_complete_q2_does_not_promote_q3_or_cone():
    value = build()
    assert value["activation_disposition"]["complete_scalar_q2_payload_assembled"] is True
    assert value["activation_disposition"]["scalar_q3_exported"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
