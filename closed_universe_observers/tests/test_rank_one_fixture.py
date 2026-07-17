from __future__ import annotations

from copy import deepcopy
import json

from closed_universe_observers import generate_rank_one_fixture as producer
from closed_universe_observers import verify_rank_one_fixture as verifier


def _input() -> dict:
    return json.loads(producer.INPUT.read_text())


def _mutate(name: str) -> tuple[dict, dict]:
    data = _input()
    mutation = next(item for item in data["mutations"] if item["name"] == name)
    mutated = deepcopy(data)
    mutated.update(mutation["patch"])
    return mutation, producer.evaluate(mutated)


def test_base_fixture_has_distinct_exact_ranks() -> None:
    result = producer.evaluate(_input())
    assert result["global_rank"] == 1
    assert result["global_fundamental_dimension"] == 1
    assert result["observer_rank"] == 2
    assert result["observer_gram"].det() == 1


def test_factorization_mutation_breaks_rank_one() -> None:
    mutation, result = _mutate("break_factorization")
    assert result["requirements"][mutation["expected_failed_requirement"]] is False
    assert result["global_rank"] == 2


def test_observer_channel_mutation_collapses_observer_rank() -> None:
    mutation, result = _mutate("remove_observer_channel")
    assert result["requirements"][mutation["expected_failed_requirement"]] is False
    assert result["observer_rank"] == 1


def test_pointer_basis_mutation_is_fail_closed_without_collapsing_rank() -> None:
    mutation, result = _mutate("rotate_away_from_pointer_basis")
    assert result["requirements"][mutation["expected_failed_requirement"]] is False
    assert result["observer_rank"] == 2


def test_reference_mutation_is_fail_closed() -> None:
    mutation, result = _mutate("collapse_reference_system")
    assert result["requirements"][mutation["expected_failed_requirement"]] is False
    assert result["observer_rank"] == 1


def test_rank_one_conclusion_mutation_enlarges_global_carrier() -> None:
    mutation, result = _mutate("enlarge_fundamental_projection")
    assert result["requirements"][mutation["expected_failed_requirement"]] is False
    assert result["global_rank"] == 2


def test_independent_replay() -> None:
    assert verifier.main() == 0
