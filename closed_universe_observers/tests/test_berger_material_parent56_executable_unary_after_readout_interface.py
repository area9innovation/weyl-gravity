import copy

import pytest

from closed_universe_observers import generate_berger_material_parent56_executable_unary_after_readout_interface as subject


def test_complete_internal_unary_and_pairing_pass():
    payload = subject.build_payload()
    unary = payload["complete_internal_q1"]
    assert unary["entry_count"] == 52
    assert unary["q1_squared_defect_count"] == unary["formal_cyclicity_defect_count"] == 0
    assert unary["pairing_rank"] == 56
    assert unary["real_defect_count"] == unary["K_commutator_defect_count"] == 0


def test_generic_and_zero_mode_restrictions_are_exact():
    payload = subject.build_payload()
    assert payload["complete_internal_q1"]["generic_rank"] == 28
    assert payload["zero_mode"]["substitution_defect_count"] == 0
    assert payload["zero_mode"]["rank"] == 24


def test_detector_map_has_rank_two_and_chain_defects_zero():
    detector = subject.build_payload()["detector_chain_map"]
    assert detector["rank"] == 2
    assert detector["internal_chain_defect_count"] == 0
    assert detector["readout_profile_chain_defect_count"] == 0
    assert detector["spatial_zero_mode_chain_defect_count"] == 0


def test_external_readout_is_typed_and_not_forced_into_56_rows():
    interface = subject.build_payload()["external_mixed_readout_interface"]
    assert interface["entry_count"] == 4
    assert interface["typing_status"] == "CERTIFIED_RELATIVE_INTERFACE_NOT_AN_INTERNAL_56_BY_56_ENTRY"
    assert all(block["internal_56_entry"] is False for block in interface["blocks"])


def test_each_mixed_entry_mutation_fails():
    blocks = subject.build_payload()["external_mixed_readout_interface"]["blocks"]
    for index in range(4):
        mutated = copy.deepcopy(blocks)
        mutated[index]["action_hessian_coefficient"] = "1"
        with pytest.raises(AssertionError):
            subject.validate_mixed_blocks(mutated)
