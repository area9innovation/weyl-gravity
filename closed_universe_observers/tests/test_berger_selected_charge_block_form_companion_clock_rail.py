import copy
from fractions import Fraction
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_selected_charge_block_form_companion_clock_rail import CERTIFICATE
from closed_universe_observers.verify_berger_selected_charge_block_form_companion_clock_rail import verify


def test_all_form_companions_and_clock_powers_are_exported() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["form_companion_rows"]) == 33
    assert all(len(row["clock_power_intervals"]) == 15 for row in value["form_companion_rows"])
    assert value["coverage"]["form_companion_complex_interval_count"] == 495


def test_all_form_companion_widths_pass() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert all(
        Fraction(power["maximum_axis_width"]) < Fraction(1, 10)
        for row in value["form_companion_rows"]
        for power in row["clock_power_intervals"]
    )


def test_charge_block_inputs_are_closed_for_every_power() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["completed_charge_block_inputs"]) == 18
    assert all(len(block["clock_power_helicity_vectors"]) == 15 for block in value["completed_charge_block_inputs"])
    assert value["flags"]["ALL_18_SELECTED_CHARGE_BLOCK_INPUTS_CLOSED"] is True


def test_deleted_form_companion_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["form_companion_rows"].pop()
    with pytest.raises((AssertionError, ValidationError)):
        verify(value)


def test_temporal_green_response_and_quantum_claims_remain_false() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False
