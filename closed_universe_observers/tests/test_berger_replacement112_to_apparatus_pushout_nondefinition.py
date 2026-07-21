import copy

import pytest

from closed_universe_observers import generate_berger_replacement112_to_apparatus_pushout_nondefinition as subject


def test_obstructed_source_makes_chain_pushout_nondefined():
    payload = subject.build_payload()
    assert payload["category_of_complexes_gate"]["source_object_status"] == "OBSTRUCTED"
    assert payload["category_of_complexes_gate"]["pushout_status"] == "NONDEFINED"


def test_separator_is_basis_independent_and_nonzero():
    separator = subject.build_payload()["basis_independent_separator"]
    assert separator["zero_property_is_basis_invariant"] is True
    assert separator["exact_specialization_rank_lower_bound"] == 1
    assert separator["defect_entry_count"] == 132 and separator["defect_position_count"] == 28


def test_all_downstream_consumers_remain_fail_closed():
    assert set(subject.build_payload()["consumer_activation"].values()) == {"NO_CERTIFIED_MAP"}


def test_success_status_mutation_is_rejected():
    terminal = subject.json.loads(subject.DEPS["terminal_replacement112"].read_text())
    payload = subject.json.loads(subject.DEPS["terminal_replacement112_payload"].read_text())
    mutated = copy.deepcopy(terminal)
    mutated["atlas_status"] = "CERTIFIED"
    with pytest.raises(AssertionError):
        subject.validate_terminal_branch(mutated, payload)


def test_zero_witness_mutation_is_rejected():
    terminal = subject.json.loads(subject.DEPS["terminal_replacement112"].read_text())
    payload = subject.json.loads(subject.DEPS["terminal_replacement112_payload"].read_text())
    mutated = copy.deepcopy(payload)
    mutated["mixed_nilpotency_obstruction"]["first_witness_nonzero"] = False
    with pytest.raises(AssertionError):
        subject.validate_terminal_branch(terminal, mutated)
