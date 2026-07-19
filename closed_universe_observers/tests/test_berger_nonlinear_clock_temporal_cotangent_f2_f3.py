from closed_universe_observers.generate_berger_nonlinear_clock_temporal_cotangent_f2_f3 import (
    build,
    cotangent_operators,
    deserialize_cotangent_operator,
    inverse_and_adjoint_audit,
    serialize_cotangent_operator,
)


def test_formal_adjoint_is_involutive_in_berger_pbw_algebra():
    audit = inverse_and_adjoint_audit()
    assert audit["formal_adjoint_involution_defect"]["linear"]["operator_key_count"] == 0
    assert audit["formal_adjoint_involution_defect"]["quadratic"]["operator_key_count"] == 0


def test_cotangent_inverse_preserves_canonical_one_form_through_f3():
    defect = inverse_and_adjoint_audit()["canonical_one_form_inverse_defect"]
    assert defect["degree_2"]["operator_key_count"] == 0
    assert defect["degree_3"]["operator_key_count"] == 0


def test_temporal_cotangent_payload_has_exact_support():
    operators = cotangent_operators()
    f2 = serialize_cotangent_operator(operators["P2"], 2)
    f3 = serialize_cotangent_operator(operators["P3"], 3)
    assert len(f2) == 93
    assert len(f3) == 135
    assert deserialize_cotangent_operator(f2, 2) == operators["P2"]
    assert deserialize_cotangent_operator(f3, 3) == operators["P3"]
    assert inverse_and_adjoint_audit()["nonholonomic_sqrt10_term_count"] > 0


def test_cotangent_mutations_are_detected():
    assert inverse_and_adjoint_audit(pointwise=True)["canonical_one_form_inverse_defect"]["degree_2"]["operator_key_count"] > 0
    assert inverse_and_adjoint_audit(omit_quadratic_inverse=True)["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] > 0
    assert inverse_and_adjoint_audit(drop_structure=True)["canonical_one_form_inverse_defect"]["degree_3"]["operator_key_count"] > 0


def test_temporal_canonical_submap_keeps_combined_consumers_closed():
    value = build()
    assert value["activation_disposition"]["temporal_BV_cotangent_lift_certified"] is True
    assert value["activation_disposition"]["combined_radial_temporal_clock_map_certified"] is False
    assert value["activation_disposition"]["scalar_q2_q3_transport_authorized"] is False
    assert value["activation_disposition"]["physical_branch_bridge_activated"] is False
