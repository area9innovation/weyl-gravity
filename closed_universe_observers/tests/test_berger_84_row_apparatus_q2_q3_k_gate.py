from __future__ import annotations

from closed_universe_observers.generate_berger_84_row_apparatus_q2_q3_k_gate import (
    build,
    gram_jacobian_two_jet_audit,
    product_two_jet_audit,
)


def test_normalized_profile_two_jet_and_mutations() -> None:
    jacobian = gram_jacobian_two_jet_audit()
    assert jacobian["first_variation_defect_count"] == 0
    assert jacobian["second_variation_defect_count"] == 0
    assert gram_jacobian_two_jet_audit(delete_quadratic_trace_term=True)["mutation_defect_count"] > 0
    product = product_two_jet_audit()
    assert product["first_jet_defect_count"] == 0
    assert product["second_jet_defect_count"] == 0
    assert product_two_jet_audit(delete_pair_partition=True)["second_jet_defect_count"] > 0


def test_apparatus_q2_q3_action_jets_are_complete_on_declared_scope() -> None:
    value = build()
    jets = value["apparatus_action_jets"]
    for family in ("rods", "memory_transport", "readout", "scalar_BV"):
        assert family in jets["lowered_cubic_tensor_C3_equals_Omega_q2"]
        assert family in jets["lowered_quartic_tensor_C4_equals_Omega_q3"]
    assert jets["identity_disposition"]["q2_cyclicity_defect_count"] == 0
    assert jets["identity_disposition"]["q3_cyclicity_defect_count"] == 0
    assert jets["identity_disposition"]["arity_three_at_r1"] == "INPUT_BLOCKED_Q4_PHI2"


def test_affine_k_obstruction_is_not_a_rank_failure() -> None:
    value = build()
    gate = value["K_Berger_gate"]
    assert not gate["ordinary_linear_action_background_preserving"]
    assert len(gate["background_components"]["rod_witnesses"]) == 2
    assert gate["background_components"]["time_dependent_Phi2_nonzero_coefficient_count"] > 0
    completion = gate["existing_rod_linear_symmetry_completion"]
    assert completion["current_real_rod_span_rank"] == 6
    assert completion["time_translation_closure_rank"] == 8
    assert not completion["constant_internal_6_by_6_completion_exists"]
    assert completion["minimal_additional_real_rod_directions"] == 2
    assert gate["q4_underdetermination_witness"]["nonzero"]
    response = value["observer_response"]
    assert response["formal_rank"] == 2
    assert response["determinant_is_unit"]


def test_claim_boundary_is_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["APPARATUS_Q2_ACTION_JET_EXPORTED"]
    assert flags["APPARATUS_Q3_ACTION_JET_EXPORTED"]
    assert flags["AFFINE_K_BERGER_THROUGH_ARITY_TWO_CERTIFIED"]
    assert not flags["AFFINE_K_BERGER_THROUGH_ARITY_THREE_CERTIFIED"]
    assert not flags["OBSERVER_EVALUATION_MORPHISM_CERTIFIED"]
    assert not flags["FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED"]
    assert not flags["QUANTUM_CLAIM"]
