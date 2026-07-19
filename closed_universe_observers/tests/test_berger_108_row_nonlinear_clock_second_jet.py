from closed_universe_observers import berger_108_row_q1_pbw_replay as replay
from closed_universe_observers import berger_108_row_nonlinear_clock_second_jet as second_jet


def _candidate():
    q1 = replay.load_q1()
    correction, parts = second_jet.candidate_completion(q1[(0, 0)], q1[(1, 0)])
    return q1, correction, parts


def test_three_second_jet_blocks_are_exactly_odd_cyclic():
    _q1, correction, parts = _candidate()
    assert {name: replay.summary(value)["operator_key_count"] for name, value in parts.items()} == {
        "radial": 21,
        "weyl": 9,
        "temporal": 65,
    }
    assert all(replay.cyclicity_defect(value) == {} for value in parts.values())
    assert replay.cyclicity_defect(correction) == {}


def test_clock_doublet_columns_cancel_freely_and_mixed_gate_stays_zero():
    q1, correction, _parts = _candidate()
    q1[(1, 0)] = replay.add_operators(q1[(1, 0)], correction)
    squared = replay.q1_squared_coefficients(q1)
    assert squared[(0, 0)] == {}
    assert squared[(0, 1)] == {}
    assert squared[(1, 1)] == {}
    assert not any(column in (3, 16) for _row, column, _word in squared[(1, 0)])
