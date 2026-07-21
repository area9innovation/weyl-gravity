import copy
import json

import pytest

from closed_universe_observers.verify_observer_tier3_fixed_point_after_historical_base_binding_repair_v1 import (
    OBSTRUCTION,
    verify_value,
)


def value() -> dict:
    return json.loads(OBSTRUCTION.read_text())


def test_exact_first_frontier_verifies():
    verify_value(value())


@pytest.mark.parametrize(
    ("path", "replacement"),
    [
        (("first_failure", "classification"), "SCIENTIFIC_CONTRADICTION"),
        (("first_failure", "test"), "closed_universe_observers/tests/test_other.py::test_other"),
        (("materialization", "hash_mismatch_count"), 1),
        (("authoritative_run", "passed_before_first_failure"), 398),
        (("flags", "AUTHORITATIVE_RUN_GREEN"), True),
        (("flags", "PAPER9_EVIDENCE_GATE_ACTIVATED"), True),
    ],
)
def test_frontier_mutations_fail_closed(path, replacement):
    mutated = copy.deepcopy(value())
    mutated[path[0]][path[1]] = replacement
    with pytest.raises(AssertionError):
        verify_value(mutated)
