from __future__ import annotations

import json

from closed_universe_observers import generate_berger_observer_interaction_import_gate as producer
from closed_universe_observers import verify_berger_observer_interaction_import_gate as verifier


def _data() -> dict:
    return json.loads(producer.INPUT.read_text())


def test_repaired_q2_import_preserves_only_the_linear_rank_two_coefficient() -> None:
    result = producer.evaluate(_data())
    assert all(result["requirements"].values())
    assert result["exported_block_count"] == 0
    assert result["missing_block_count"] == 14
    assert result["minimum_required_maximum_arity"] == 3


def test_each_interaction_gate_mutation_fails_closed() -> None:
    data = _data()
    for mutation in data["mutations"]:
        result = producer.evaluate(data, mutation["patch"])
        assert result["requirements"][mutation["expected_failed_requirement"]] is False


def test_missing_apparatus_rows_prevent_cyclicity_and_quotient_promotion() -> None:
    certificate = producer.build()
    flags = certificate["flags"]
    assert flags["REPAIRED_64_ROW_Q2_IMPORTED_EXACTLY"] is True
    assert flags["LINEAR_RANK_TWO_RECORD_TRANSFER_PRESERVED"] is True
    assert flags["MAXWELL_STRESS_BACKREACTION_VERTEX_AVAILABLE"] is True
    assert flags["OBSERVER_APPARATUS_ROWS_ADJOINED_TO_REPAIRED_COMPLEX"] is False
    assert flags["EXTENDED_CYCLICITY_CERTIFIED"] is False
    assert flags["BACKREACTED_RANK_TWO_RECORDS_CERTIFIED"] is False
    assert flags["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is False


def test_rod_dependent_memory_readout_requires_q3() -> None:
    certificate = producer.build()
    assert certificate["arity_analysis"]["minimum_required_maximum_arity"] == 3
    assert certificate["arity_analysis"]["q2_only_extension_sufficient"] is False


def test_independent_interaction_gate_replay() -> None:
    assert verifier.main() == 0
