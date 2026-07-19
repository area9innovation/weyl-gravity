from fractions import Fraction

from closed_universe_observers.generate_berger_108_row_shifted_q2_phi2_pbw_overlay import (
    build,
    payload_document,
)


def test_shifted_q2_contracts_first_slot_of_both_pinned_payloads_exactly():
    payload = payload_document()
    assert payload["raw_contraction_count"] == 92965
    assert payload["normalized_term_count"] == 92965
    assert payload["nonzero_matrix_position_count"] == 310


def test_shifted_q2_retains_fourth_order_unary_and_phi2_jets():
    orders = {(row["input_order"], row["Phi2_order"]) for row in payload_document()["derivative_order_histogram"]}
    assert (4, 0) in orders
    assert (0, 5) in orders


def test_known_physical_principal_witness_remains_pinned():
    value = build()
    assert value["principal_witness"]["contracted_coefficient"] == "623/324"
    assert value["identity_disposition"]["both_symmetric_slots_mutation_detected"] is True


def test_complete_q1_remains_fail_closed_on_local_rod_hessian():
    flags = build()["flags"]
    assert flags["SCALAR_SHIFTED_Q2_PHI2_PBW_OVERLAY_EXPORTED"]
    assert not flags["SCALAR_ROD_LOCAL_HESSIAN_PBW_OVERLAY_EXPORTED"]
    assert not flags["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]
