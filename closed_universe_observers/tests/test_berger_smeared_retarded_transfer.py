from __future__ import annotations

import json

from closed_universe_observers import generate_berger_smeared_retarded_transfer as producer
from closed_universe_observers import verify_berger_smeared_retarded_transfer as verifier


def _data() -> dict:
    return json.loads(producer.INPUT.read_text())


def test_physical_retarded_transfer_has_rank_two() -> None:
    result = producer.evaluate(_data())
    assert all(result["requirements"].values())
    assert result["matching_matrix"] == producer.sp.eye(2)
    assert result["response_matrix"] == [["C_00", "0"], ["0", "C_11"]]
    assert result["determinant"] == "C_00*C_11"
    assert result["structural_rank"] == 2


def test_each_transfer_mutation_fails_closed() -> None:
    data = _data()
    for mutation in data["mutations"]:
        result = producer.evaluate(producer._patched(data, mutation["patch"]))
        assert result["requirements"][mutation["expected_failed_requirement"]] is False


def test_rank_two_does_not_promote_localized_emitters_or_quotient_descent() -> None:
    certificate = producer.build()
    assert certificate["flags"]["SMEARED_RETARDED_TRANSFER_MATRIX_RANK_TWO"] is True
    assert certificate["flags"]["TWO_CAUSALLY_ACQUIRED_MEMORY_RECORDS_DISTINGUISHABLE"] is True
    assert certificate["flags"]["SPATIALLY_LOCALIZED_EMITTER_WORLDTUBES"] is False
    assert certificate["flags"]["D_DESCENT_WITH_SOURCE_ROD_MEMORY_SECTOR_CERTIFIED"] is False
    assert certificate["flags"]["CLASSICAL_OBSERVER_MAP_CERTIFIED"] is False


def test_independent_transfer_replay() -> None:
    assert verifier.main() == 0
