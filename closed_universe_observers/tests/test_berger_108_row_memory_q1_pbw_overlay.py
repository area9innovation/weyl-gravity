from fractions import Fraction

from closed_universe_observers.generate_berger_108_row_memory_q1_pbw_overlay import (
    build,
    field_strength_operator,
    payload_document,
)
from closed_universe_observers.berger_108_row_component_jet_contract import scale


def test_all_sixteen_memory_first_jet_blocks_are_scalarized():
    overlay = payload_document()
    assert overlay["block_count"] == 16
    assert overlay["row_support"] == [59, 60, 61, 62, 80, 81, 82, 83]
    assert overlay["column_support"] == [55, 56, 57, 58, 70, 71, 72, 73]


def test_every_bidegree_is_present_for_both_channels():
    ids = {block["id"] for block in payload_document()["blocks"]}
    for channel in (0, 1):
        for degree in ("Q00", "Q01", "Q10", "Q11"):
            assert any(block.startswith(f"memory{channel}_") and block.endswith(degree) for block in ids)


def test_profile_adjoints_export_coefficient_jets():
    blocks = {block["id"]: block for block in payload_document()["blocks"]}
    for channel in (0, 1):
        for degree in ("Q01", "Q11"):
            factors = [
                factor
                for entry in blocks[f"memory{channel}_profile_adjoint_{degree}"]["entries"]
                for term in entry["terms"]
                for factor in term["coefficient_factors"]
            ]
            assert any(sum(factor["spacetime_multiindex"]) > 0 for factor in factors)


def test_complete_q1_remains_fail_closed_on_rod_overlay():
    flags = build()["flags"]
    assert flags["SCALAR_MEMORY_Q1_PBW_OVERLAY_EXPORTED"]
    assert not flags["SCALAR_ROD_GRAVITY_Q1_PBW_OVERLAY_EXPORTED"]
    assert not flags["SUPPORT_LOCAL_108_ROW_PBW_Q1_PAYLOAD_EXPORTED"]


def test_invariant_frame_field_strength_has_negative_cartan_term():
    operator = field_strength_operator(0, varied=True)
    derivative_coefficient = operator[82, 57, (1,)]  # F_12 contains e1 A2
    algebraic_coefficient = operator[82, 58, ()]     # and -(3 sqrt(10)/20) A3
    assert algebraic_coefficient == scale(
        derivative_coefficient, (Fraction(0), Fraction(-3, 20))
    )
