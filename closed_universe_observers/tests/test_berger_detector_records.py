from __future__ import annotations

import json

from closed_universe_observers import generate_berger_detector_records as producer
from closed_universe_observers import verify_berger_detector_records as verifier


def _data() -> dict:
    return json.loads(producer.INPUT.read_text())


def test_two_localized_clock_labelled_records_are_independent() -> None:
    result = producer.evaluate(_data())
    assert all(result["requirements"].values())
    assert result["record_matrix"].rank() == 2
    assert result["clock_ordered_after_emitter"] is True


def test_each_detector_mutation_fails_its_declared_gate() -> None:
    data = _data()
    for mutation in data["mutations"]:
        result = producer.evaluate(producer._patched(data, mutation["patch"]))
        assert result["requirements"][mutation["expected_failed_requirement"]] is False


def test_pointwise_retarded_two_click_gate_remains_fail_closed() -> None:
    certificate = producer.build()
    assert certificate["flags"]["TWO_LOCALIZED_CLOCK_LABELLED_RECORD_FUNCTIONALS"] is True
    assert certificate["flags"]["TWO_NONZERO_RETARDED_RECORD_VALUES"] is False
    assert certificate["flags"]["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is False


def test_independent_detector_record_replay() -> None:
    assert verifier.main() == 0
