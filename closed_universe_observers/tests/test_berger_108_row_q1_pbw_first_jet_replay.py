from fractions import Fraction

from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers.generate_berger_108_row_q1_pbw_first_jet_replay import (
    remove_euler_to_bv_bridge,
)


def test_repaired_zeroth_order_is_cyclic_and_nilpotent():
    q00 = replay.load_q1()[(0, 0)]
    assert replay.cyclicity_defect(q00) == {}
    assert replay.compose(q00, q00) == {}


def test_unraised_euler_rows_reproduce_the_detected_interface_mutation():
    q00 = remove_euler_to_bv_bridge(replay.load_q1()[(0, 0)])
    assert replay.summary(replay.compose(q00, q00))["operator_key_count"] == 24
    assert replay.summary(replay.cyclicity_defect(q00))["operator_key_count"] == 102


def test_strict_first_jet_sign_bound_is_negative():
    upper = Fraction(27, 32) * Fraction(5, 72) - Fraction(2921, 480)
    assert upper < 0
