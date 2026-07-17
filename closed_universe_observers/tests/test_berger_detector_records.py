from __future__ import annotations

import json

from closed_universe_observers import generate_berger_detector_records as producer
from closed_universe_observers import verify_berger_detector_records as verifier


def _data() -> dict:
    return json.loads(producer.INPUT.read_text())


def test_rods_smearings_causal_centers_and_memory_are_certified() -> None:
    result = producer.evaluate(_data())
    assert all(result["requirements"].values())
    assert result["record_matrix"].rank() == 2
    assert result["incidence_residuals"] == [0, 0]
    assert result["travel_distances"] == [producer._q("1/4"), producer._q("1/2")]


def test_each_detector_mutation_fails_its_declared_gate() -> None:
    data = _data()
    for mutation in data["mutations"]:
        result = producer.evaluate(producer._patched(data, mutation["patch"]))
        assert result["requirements"][mutation["expected_failed_requirement"]] is False


def test_smeared_retarded_transfer_gate_remains_fail_closed() -> None:
    certificate = producer.build()
    assert certificate["flags"]["TWO_LOCALIZED_CLOCK_LABELLED_DETECTOR_SMEARINGS"] is True
    assert certificate["flags"]["PERSISTENT_PROBE_MEMORY_REGISTERS"] is True
    assert certificate["flags"]["SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO"] is False
    assert certificate["flags"]["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is False
    assert certificate["next_transfer_gate"]["matrix"] == "M_ab=Q_a[d G_ret J_b]"
    assert certificate["probe_memory_registers"]["equations"][0] == "d_Theta m_a=q_a(Theta;F)"


def test_independent_detector_record_replay() -> None:
    assert verifier.main() == 0
