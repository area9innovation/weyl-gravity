from __future__ import annotations

from closed_universe_observers.generate_berger_108_row_emitter_unary_recoil import build, carrier_audit, massive_two_form_green_audit, recoil_green_audit, unary_identity_audit


def test_emitter_rows_and_pairing_are_complete() -> None:
    carrier = carrier_audit()
    assert carrier["degree_ranks_minus1_0_1_2"] == [6, 48, 48, 6]
    assert carrier["new_pairing_rank"] == 24
    assert not carrier_audit(drop_last_pair=True)["new_pairing_nondegenerate"]


def test_massive_two_form_green_formula_is_two_sided() -> None:
    assert massive_two_form_green_audit()["left_right_defect_count"] == 0
    assert massive_two_form_green_audit(drop_constraint_term=True)["left_right_defect_count"] > 0


def test_unary_identities_and_first_recoil_green_close() -> None:
    unary = unary_identity_audit()
    recoil = recoil_green_audit()
    assert unary["gauge_nilpotency_defect_count"] == 0
    assert unary["unary_cyclicity_defect_count"] == 0
    assert recoil["left_right_defect_count_through_g2"] == 0
    assert recoil_green_audit(delete_second_order=True)["left_right_defect_count_through_g2"] > 0


def test_scope_is_fail_closed() -> None:
    flags = build()["flags"]
    assert flags["108_ROW_Q1_CERTIFIED"]
    assert flags["FIRST_FORMAL_EMITTER_RECOIL_GREEN_OPERATOR_COMPUTED"]
    assert not flags["FULL_108_ROW_CAUSAL_CHAIN_CONTRACTION_CERTIFIED"]
    assert not flags["DYNAMICAL_EMITTER_RECORD_RANK_TWO_CERTIFIED"]
    assert not flags["DETECTOR_RECOIL_COEFFICIENT_EVALUATED"]
    assert not flags["EMITTER_STRESS_BACKREACTION_INCLUDED"]
    assert not flags["QUANTUM_CLAIM"]
