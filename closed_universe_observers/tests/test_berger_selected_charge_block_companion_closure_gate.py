import copy
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_selected_charge_block_companion_closure_gate import CERTIFICATE
from closed_universe_observers.verify_berger_selected_charge_block_companion_closure_gate import verify


def test_selected_rail_is_not_charge_block_closed() -> None:
    value = json.loads(CERTIFICATE.read_text())
    coverage = value["coverage"]
    assert coverage["selected_real_form_entry_count"] == 18
    assert coverage["distinct_charge_block_count"] == 18
    assert coverage["missing_on_support_real_form_entry_count"] == 33
    assert value["flags"]["SELECTED_INPUT_RAIL_CHARGE_BLOCK_CLOSED"] is False


def test_structural_zeros_are_separate_from_missing_companions() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["coverage"]["structural_zero_real_form_entry_count"] == 27
    assert value["coverage"]["charge_block_real_entry_union_count"] == 78


def test_exact_six_scalar_row_activation_gate() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["missing_scalar_rows"] == [
        [1023, 129], [1023, 257], [1023, 385],
        [1025, 130], [1025, 258], [1025, 386],
    ]
    assert value["coverage"]["required_scalar_row_count_for_missing_entries"] == 18
    assert value["coverage"]["already_certified_scalar_row_count"] == 12


def test_deleted_missing_companion_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["missing_on_support_real_form_entries"].pop()
    with pytest.raises((AssertionError, ValidationError)):
        verify(value)


def test_green_response_and_quantum_claims_remain_false() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False
