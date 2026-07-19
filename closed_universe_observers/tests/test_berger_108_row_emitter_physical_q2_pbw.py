from closed_universe_observers.generate_berger_108_row_emitter_physical_q2_pbw import build, metric_jet_audit, payload_document, q1_hessian_recovery_audit


def test_quadratic_action_recovers_certified_emitter_q1():
    assert q1_hessian_recovery_audit()["q1_hessian_recovery_defect_count"] == 0


def test_metric_form_pairing_first_jets_are_direct():
    assert metric_jet_audit()["metric_bilinear_first_jet_defect_count"] == 0


def test_payload_has_all_physical_source_families():
    value = payload_document()
    assert set(value["source_family_counts"]) == {"free_kinetic_metric", "free_mass_metric", "interaction_clock_switch", "interaction_metric"}
    assert value["operator_key_count"] > 0
    assert value["serialized_term_count"] >= value["operator_key_count"]


def test_diff_bv_and_complete_q2_remain_closed():
    value = build()
    assert value["activation_disposition"]["emitter_physical_q2_subblock_exported"] is True
    assert value["activation_disposition"]["emitter_diff_BV_q2_subblock_exported"] is False
    assert value["activation_disposition"]["complete_emitter_q2_exported"] is False
    assert value["activation_disposition"]["detector_response_on_second_order_cone_authorized"] is False
