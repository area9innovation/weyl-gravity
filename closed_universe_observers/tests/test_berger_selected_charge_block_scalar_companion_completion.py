import copy
from fractions import Fraction
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_selected_charge_block_scalar_companion_completion import CERTIFICATE
from closed_universe_observers.verify_berger_selected_charge_block_scalar_companion_completion import verify


def test_exact_six_scalar_rows_are_evaluated() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert [(row["two_j"], row["basis_index"]) for row in value["newly_evaluated_scalar_rows"]] == [
        (1023, 129), (1023, 257), (1023, 385),
        (1025, 130), (1025, 258), (1025, 386),
    ]


def test_new_widths_pass_and_high_rows_use_radial_refinement() -> None:
    value = json.loads(CERTIFICATE.read_text())
    rows = value["newly_evaluated_scalar_rows"]
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in rows)
    assert [row["radial_subdivisions"] for row in rows] == [64, 64, 128, 64, 64, 128]


def test_complete_scalar_union_has_eighteen_rows() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert len(value["complete_scalar_input_rows"]) == 18
    assert value["coverage"]["previously_certified_scalar_row_count"] == 12


def test_deleted_new_row_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["newly_evaluated_scalar_rows"].pop()
    with pytest.raises((AssertionError, ValidationError)):
        verify(value)


def test_form_green_and_response_claims_remain_false() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["flags"]["THIRTY_THREE_ON_SUPPORT_FORM_COMPANIONS_EVALUATED"] is False
    assert value["flags"]["TEMPORAL_FUNCTIONAL_CALCULUS_APPLIED"] is False
    assert value["flags"]["GREEN_IMAGES_EVALUATED"] is False
    assert value["flags"]["DETECTOR_RESPONSE_EVALUATED"] is False
    assert value["flags"]["QUANTUM_CLAIM"] is False
