import copy
from fractions import Fraction
import json

import pytest

from closed_universe_observers.generate_berger_selected_p0_polarized_form_intervals import CERTIFICATE
from closed_universe_observers.verify_berger_selected_p0_polarized_form_intervals import verify


def test_all_eighteen_selected_p0_form_rows_are_narrow() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["polarized_form_rows"]) == 18
    assert all(
        Fraction(row["polarized_interval"]["maximum_axis_width"]) < Fraction(1, 10)
        for row in value["polarized_form_rows"]
    )


def test_all_scalar_term_applications_are_serialized() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert sum(row["recurrence_term_count"] for row in value["polarized_form_rows"]) == 54
    assert value["flags"]["ALL_FIFTY_FOUR_SCALAR_TERM_APPLICATIONS_EXPORTED"] is True


def test_deleted_term_coverage_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["polarized_form_rows"][0]["term_applications"].pop()
    with pytest.raises(AssertionError):
        verify(value)


def test_higher_clock_and_green_claims_remain_false() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["flags"]["ALL_CLOCK_POWERS_AND_COMPLETE_FORM_RAIL_EVALUATED"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False
