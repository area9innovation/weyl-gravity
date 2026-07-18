from __future__ import annotations

from closed_universe_observers.generate_berger_108_row_emitter_causal_chain import build, graded_chain_fixture


def test_gauge_complete_graded_chain_closes_through_g2() -> None:
    fixture = graded_chain_fixture()
    assert fixture["q_squared_defect_count"] == 0
    assert fixture["left_green_defect_count_through_g2"] == 0
    assert fixture["right_green_defect_count_through_g2"] == 0
    assert fixture["chain_homotopy_defect_count_through_g2"] == 0
    assert fixture["homotopy_degree_minus_one"]


def test_chain_mutations_are_detected() -> None:
    assert graded_chain_fixture(delete_quadratic_green=True)["chain_homotopy_defect_count_through_g2"] > 0
    assert not graded_chain_fixture(delete_k1_witness=True)["unperturbed_wave_invertible"]


def test_scope_remains_coefficientwise_and_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["108_ROW_COEFFICIENTWISE_CAUSAL_CHAIN_HOMOTOPY_THROUGH_G2_CERTIFIED"]
    assert not flags["UNQUALIFIED_FULL_108_ROW_CAUSAL_CHAIN_CONTRACTION_CERTIFIED"]
    assert not flags["FINITE_PARAMETER_108_ROW_GREEN_HYPERBOLICITY_CERTIFIED"]
    assert not flags["DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED"]
    assert not flags["QUANTUM_CLAIM"]
