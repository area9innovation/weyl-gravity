from closed_universe_observers.generate_berger_nonlinear_clock_radial_canonical_map_f2_f3 import (
    build, exact_chart_audit, taylor_entries,
)


def test_exact_radial_chart_and_inverse():
    audit = exact_chart_audit()
    assert audit["metric_map_defect_count"] == 0
    assert audit["inverse_defect_count"] == 0


def test_cotangent_lift_preserves_canonical_one_form():
    cotangent = exact_chart_audit()["cotangent_lift"]
    assert cotangent["dH_coefficient_defect_count"] == 0
    assert cotangent["dR_coefficient_defect_count"] == 0
    assert exact_chart_audit(omit_radial_cotangent=True)["cotangent_lift"]["dR_coefficient_defect_count"] > 0


def test_factorial_taylor_payload_has_complete_support():
    entries = taylor_entries()
    assert len(entries["F2"]) == 38
    assert len(entries["F3"]) == 38
    assert exact_chart_audit(delete_cubic_trace=True)["metric_map_defect_count"] > 0


def test_radial_subgate_does_not_activate_temporal_consumers():
    value = build()
    assert value["atlas_status"] == "CERTIFIED"
    assert value["activation_disposition"]["radial_F2_F3_certified"] is True
    assert value["activation_disposition"]["temporal_F2_F3_certified"] is False
    assert value["activation_disposition"]["scalar_q2_q3_transport_authorized"] is False
    assert value["activation_disposition"]["physical_branch_bridge_activated"] is False
