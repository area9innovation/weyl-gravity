from __future__ import annotations

from closed_universe_observers.generate_berger_84_row_normalized_profile_mixed_unary import (
    build,
    mixed_green_audit,
    normalization_audit,
)


def test_transverse_normalization_and_coarea_variation() -> None:
    value = normalization_audit()
    assert value["normalization_defect_count"] == 0
    assert value["event_specialization"]["d1_plus_sigma_a"] == "-Phi2_00/2"
    assert value["jacobian_deletion_mutation"]["detected_for_both_channels"]


def test_mixed_q11_is_exact_local_and_cyclic() -> None:
    value = build()
    profile = value["mixed_Q11_profile"]
    assert profile["bidegree"] == [1, 1]
    assert profile["nilpotency_defect_count"] == 0
    assert profile["cyclicity_defect_count"] == 0
    assert profile["nonzero_Q11_operator_block_count"] == 4
    assert profile["all_other_Q11_carrier_blocks_zero"]
    assert profile["all_84_row_mixed_nilpotency_defect_count"] == 0
    assert profile["all_84_row_mixed_cyclicity_defect_count"] == 0
    assert profile["detector_block_local"]
    assert profile["cross_channel_profile_terms"] == 0


def test_mixed_green_coefficient_and_mutation() -> None:
    value = mixed_green_audit()
    assert value["left_inverse_defect_count_at_r_kappa"] == 0
    assert value["right_inverse_defect_count_at_r_kappa"] == 0
    mutant = mixed_green_audit(delete_direct_q11_term=True)
    assert mutant["left_inverse_defect_count_at_r_kappa"] + mutant["right_inverse_defect_count_at_r_kappa"] > 0


def test_claim_boundary_stays_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["84_ROW_COEFFICIENTWISE_BIDEGREE_FIRST_JET_CERTIFIED"]
    assert not flags["FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED"]
    assert not flags["84_ROW_Q2_Q3_CERTIFIED"]
    assert not flags["OBSERVER_EVALUATION_MORPHISM_CERTIFIED"]
    assert not flags["QUANTUM_CLAIM"]
