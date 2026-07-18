import sympy as sp

from closed_universe_observers.generate_berger_spacetime_form_block_sign_bridge import (
    block_audit,
    spacetime_d,
    spacetime_delta,
)


def test_spacetime_d_and_delta_are_nilpotent_on_a_nontrivial_block():
    row = block_audit(2)
    assert not any(row["d_squared_defect_counts_degrees_0_to_2"])
    assert not any(row["delta_squared_defect_counts_degrees_2_to_4"])


def test_maxwell_and_emitter_wave_blocks_diagonalize():
    row = block_audit(3)
    assert row["wave_diagonalization_defect_counts_degrees_1_2"] == [0, 0]


def test_wrong_temporal_coderivative_sign_is_detected():
    row = block_audit(1, wrong_time_sign=True)
    assert any(row["wave_diagonalization_defect_counts_degrees_1_2"])


def test_spacetime_block_shapes_match_form_splitting():
    z = sp.symbols("z")
    # two_j=1 has spatial dimensions (2,6,6,2)
    assert spacetime_d(1, 1, z).shape == (12, 8)
    assert spacetime_delta(1, 2, z).shape == (8, 12)
