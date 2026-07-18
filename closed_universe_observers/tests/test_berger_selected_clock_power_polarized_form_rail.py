import copy
from fractions import Fraction
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_selected_clock_power_polarized_form_rail import CERTIFICATE
from closed_universe_observers.verify_berger_selected_clock_power_polarized_form_rail import verify


def test_all_selected_form_clock_powers_are_exported() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["selected_form_rows"]) == 18
    assert all(len(row["clock_power_intervals"]) == 15 for row in value["selected_form_rows"])
    assert value["coverage"]["complex_interval_count"] == 270


def test_all_clock_power_widths_remain_below_gate() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert all(Fraction(width) < Fraction(1, 10) for width in value["maximum_axis_width_by_clock_power"].values())


def test_p0_source_is_reproduced_and_no_independence_is_assumed() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["coverage"]["p0_exact_reproduction_defect_count"] == 0
    assert value["joint_clock_weighting"]["independence_assumption"] is False


def test_deleted_p28_power_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    for row in value["selected_form_rows"]:
        row["clock_power_intervals"].pop()
    with pytest.raises((AssertionError, ValidationError)):
        verify(value)


def test_mutated_row_metadata_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["selected_form_rows"][0]["coordinate"] = "mutated_coordinate"
    with pytest.raises(AssertionError):
        verify(value)


def test_green_and_complete_form_claims_remain_false() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["flags"]["COMPLETE_FORM_RAIL_EVALUATED"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False
