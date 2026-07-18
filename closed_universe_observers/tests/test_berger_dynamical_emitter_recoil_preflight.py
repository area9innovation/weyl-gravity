from __future__ import annotations

from closed_universe_observers.generate_berger_dynamical_emitter_recoil_preflight import build, formal_rank_stability_audit, preparation_underdetermination_audit, recoil_order_audit


def test_first_emitter_data_recoil_is_absolute_g3_not_g2() -> None:
    audit = recoil_order_audit()
    assert audit["left_right_inverse_defect_count_through_g3"] == 0
    assert audit["absolute_g2_term_zero"]
    assert audit["cubic_matches_leading_times_relative_g2_self_energy"]


def test_recoil_order_mutations_are_detected() -> None:
    assert recoil_order_audit(delete_cubic=True)["left_right_inverse_defect_count_through_g3"] > 0
    assert recoil_order_audit(insert_quadratic=True)["left_right_inverse_defect_count_through_g3"] > 0


def test_recoil_coefficient_remains_input_blocked() -> None:
    audit = preparation_underdetermination_audit()
    assert audit["same_nonzero_leading_response"]
    assert audit["different_recoil_response"]
    flags = build()["flags"]
    assert flags["FIRST_DETECTOR_RECOIL_ABSOLUTE_G3_OPERATOR_COMPUTED"]
    assert not flags["DETECTOR_RECOIL_NUMERICAL_COEFFICIENT_EVALUATED"]
    assert flags["DYNAMICAL_EMITTER_LEADING_RECORD_MATRIX_RANK_TWO_RETAINED"]
    assert formal_rank_stability_audit()["rank_two_over_formal_recoil_ring"]
    assert not formal_rank_stability_audit(erase_second_leading_diagonal=True)["rank_two_over_formal_recoil_ring"]
