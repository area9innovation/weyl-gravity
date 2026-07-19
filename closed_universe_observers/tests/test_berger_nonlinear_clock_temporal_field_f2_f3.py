from closed_universe_observers.generate_berger_nonlinear_clock_temporal_field_f2_f3 import (
    TemporalJetChart,
    build,
    field_chart_audit,
    phase_inverse_audit,
)


def test_clock_phase_inverse_is_exact_through_cubic_degree():
    assert phase_inverse_audit()["residual_term_count"] == 0
    assert phase_inverse_audit(omit_cubic_terms=True)["residual_term_count"] > 0


def test_temporal_metric_pullback_reproduces_linear_dressing():
    audit = field_chart_audit()
    assert audit["linear_metric_defect_count"] == 0
    assert audit["quadratic_monomial_count"] == 36
    assert audit["cubic_monomial_count"] == 96


def test_factorial_pbw_payload_has_complete_support():
    chart = TemporalJetChart()
    payload = chart.payload()
    assert len(payload["F2"]) == 36
    assert len(payload["F3"]) == 96
    assert all(atom["row"] in range(5, 17) for key in payload for entry in payload[key] for atom in entry["inputs"])
    assert all(len(atom["pbw"]) == 4 for key in payload for entry in payload[key] for atom in entry["inputs"])
    assert chart.payload_reconstruction_audit()["defect_component_count"] == 0
    assert chart.payload_reconstruction_audit(use_full_arity_factorial=True)["defect_component_count"] > 0


def test_temporal_field_mutations_are_detected():
    audit = field_chart_audit()
    assert field_chart_audit(omit_quadratic_inverse_shift=True)["correction_expressions"] != audit["correction_expressions"]
    assert field_chart_audit(flip_inverse_jacobian_sign=True)["linear_metric_defect_count"] > 0


def test_field_subgate_keeps_cotangent_and_consumers_fail_closed():
    value = build()
    assert value["atlas_status"] == "CERTIFIED"
    assert value["activation_disposition"]["temporal_field_F2_F3_certified"] is True
    assert value["activation_disposition"]["temporal_BV_cotangent_lift_certified"] is False
    assert value["activation_disposition"]["scalar_q2_q3_transport_authorized"] is False
    assert value["activation_disposition"]["physical_branch_bridge_activated"] is False
