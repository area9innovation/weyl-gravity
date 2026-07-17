from __future__ import annotations

from closed_universe_observers import generate_berger_retained_observer_k_descent_gate as producer
from closed_universe_observers import verify_berger_retained_observer_k_descent_gate as verifier


def test_gate_finds_exact_missing_apparatus_carrier() -> None:
    result = producer.build("HEAD")
    extension = result["required_apparatus_extension"]
    assert extension["required_total_row_count"] == 84
    assert extension["new_cyclic_row_pairs"] == 10
    assert extension["retained36_overlap"] == []


def test_nonzero_k_rod_witnesses_are_inside_detector_windows() -> None:
    result = producer.build("HEAD")
    witnesses = result["exact_k_rod_witnesses"]["witnesses"]
    assert len(witnesses) == 2
    assert all(row["inside_detector_window"] and row["sign"] == "strictly_negative" for row in witnesses)


def test_gate_is_fail_closed_without_becoming_global_no_go() -> None:
    flags = producer.build("HEAD")["flags"]
    assert flags["RETAINED36_OBSERVER_VERTEX_TYPED"] is False
    assert flags["RETAINED36_K_DESCENT_CERTIFIED"] is False
    assert flags["APPARATUS_84_ROW_COMPLEX_REQUIRED"] is True
    assert flags["APPARATUS_84_ROW_COMPLEX_CERTIFIED"] is False
    assert flags["GLOBAL_OBSERVER_PROGRAMME_NO_GO"] is False


def test_independent_replay() -> None:
    assert verifier.main() == 0
