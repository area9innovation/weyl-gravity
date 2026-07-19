from closed_universe_observers.generate_berger_nonlinear_clock_combined_canonical_map_f2_f3 import build


def test_combined_chart_reproduces_both_certified_restrictions():
    audit = build()["geometric_definition"]["restriction_audit"]
    assert audit["radial_restriction_defect_count"] == 0
    assert audit["temporal_restriction_defect_count"] == 0


def test_combined_chart_contains_required_cross_terms():
    value = build()
    assert value["field_payload"]["F2_entry_count"] == 55
    assert value["field_payload"]["F3_entry_count"] == 174
    assert value["field_payload"]["reconstruction_defect_counts"] == {"F2": 0, "F3": 0}
    assert value["geometric_definition"]["restriction_audit"]["mixed_radial_temporal_monomial_counts"] == {"degree_2": 5, "degree_3": 64}


def test_combined_cotangent_lift_is_canonical_and_reconstructs():
    value = build()
    assert value["cotangent_payload"]["F2_entry_count"] == 132
    assert value["cotangent_payload"]["F3_entry_count"] == 268
    assert value["canonical_audit"]["adjoint_involution_defects"]["linear"]["operator_key_count"] == 0
    assert value["canonical_audit"]["adjoint_involution_defects"]["quadratic"]["operator_key_count"] == 0
    assert value["canonical_audit"]["canonical_inverse_defects"]["degree_2"]["operator_key_count"] == 0
    assert value["canonical_audit"]["canonical_inverse_defects"]["degree_3"]["operator_key_count"] == 0
    assert value["cotangent_payload"]["reconstruction_defects"]["F2"]["operator_key_count"] == 0
    assert value["cotangent_payload"]["reconstruction_defects"]["F3"]["operator_key_count"] == 0


def test_combined_map_authorizes_only_interaction_regeneration():
    disposition = build()["activation_disposition"]
    assert disposition["combined_clock_canonical_map_certified"] is True
    assert disposition["scalar_q2_q3_transport_authorized"] is True
    assert disposition["scalar_q2_q3_payload_exported"] is False
    assert disposition["detector_response_on_second_order_cone_authorized"] is False
    assert disposition["physical_branch_bridge_activated"] is False
