from __future__ import annotations

from closed_universe_observers.generate_berger_affine_k_observer_morphism import build, record_covariance_specialization, ward_specialization


def test_fifth_derivative_ward_contraction_and_mutation() -> None:
    assert ward_specialization()["defect_count"] == 0
    assert ward_specialization(delete_q4_contraction=True)["defect_count"] > 0


def test_affine_observer_morphism_is_rank_two() -> None:
    value = build()
    assert value["observer_morphism"]["formal_rank"] == 2
    assert value["observer_morphism"]["distinguishable_records"]
    assert value["flags"]["COEFFICIENTWISE_OBSERVER_EVALUATION_MORPHISM_CERTIFIED"]
    assert record_covariance_specialization()["K_covariance_defects"] == ["0", "0"]
    assert record_covariance_specialization()["rank"] == 2


def test_scope_excludes_full_q4_and_fixed_background_descent() -> None:
    flags = build()["flags"]
    assert flags["AFFINE_K_Q4_K0_CONTRACTION_CERTIFIED"]
    assert not flags["FULL_Q4_EXPORTED"]
    assert not flags["FIXED_BACKGROUND_LINEAR_K_DESCENT_CERTIFIED"]
    assert not flags["FINITE_R_84_ROW_GREEN_HYPERBOLICITY_CERTIFIED"]
    assert not flags["QUANTUM_CLAIM"]
