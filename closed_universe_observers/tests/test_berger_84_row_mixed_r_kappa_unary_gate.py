from __future__ import annotations

from closed_universe_observers.generate_berger_84_row_mixed_r_kappa_unary_gate import (
    build,
    inverse_first_variation_audit,
)
from closed_universe_observers.verify_berger_84_row_mixed_r_kappa_unary_gate import (
    _independent_transport,
    _semantic_boundary,
    verify,
)


def test_transport_belongs_to_q10_not_q11() -> None:
    value = build()
    assert value["bidegree_audit"]["delta_T_bidegree"] == [1, 0]
    assert value["bidegree_audit"]["delta_B_bidegree"] == [1, 1]
    assert value["bidegree_audit"]["prior_assignment_delta_T_to_Q11_rejected"]


def test_exact_phi2_transport_and_frozen_adjoint() -> None:
    value = build()
    _independent_transport(value)
    transport = value["q10_memory_transport"]
    assert transport["reality_defect_count"] == 0
    assert sum(len(entries) for entries in transport["frequency_sectors"]["zero"]["delta_T_derivative_coefficients_e1_e2_e3"]) == 0
    assert sum(len(entries) for entries in transport["frequency_sectors"]["positive"]["delta_T_derivative_coefficients_e1_e2_e3"]) == 11
    assert all(sector["density_transport_defect_count"] == 0 for sector in transport["frequency_sectors"].values())


def test_clock_green_first_variation_is_two_sided() -> None:
    audit = inverse_first_variation_audit()
    assert audit["left_inverse_defect_count_at_r"] == 0
    assert audit["right_inverse_defect_count_at_r"] == 0
    mutant = inverse_first_variation_audit(delete_correction=True)
    assert mutant["left_inverse_defect_count_at_r"] + mutant["right_inverse_defect_count_at_r"] > 0


def test_profile_density_missing_object_blocks_q11() -> None:
    value = build()
    gate = value["q11_profile_gate"]
    assert gate["status"] == "INPUT_BLOCKED_NORMALIZED_PROFILE_METRIC_VARIATION_UNEXPORTED"
    assert gate["missing_input_fields"] == [
        "metric_normalization_measure",
        "metric_variation_of_log_density",
        "normalized_density_definition",
    ]
    assert gate["underdetermination_witness"]["independent_channel_defect_count"] == 2
    assert not gate["mixed_Q11_computed"]


def test_fail_closed_boundary_and_independent_verifier() -> None:
    value = build()
    _semantic_boundary(value)
    assert not value["flags"]["MIXED_EPSILON_R2_KAPPA_UNARY_CERTIFIED"]
    assert verify() == value
