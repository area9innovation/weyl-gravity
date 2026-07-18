import copy
from fractions import Fraction
import json

import pytest

from closed_universe_observers.generate_berger_polarization_recurrence_scalar_closure import CERTIFICATE
from closed_universe_observers.verify_berger_polarization_recurrence_scalar_closure import verify


def test_recurrence_closure_has_twelve_scalar_rows() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["form_selection"]["detector_component_entry_count"] == 18
    assert value["scalar_closure"]["required_row_count"] == 12
    assert len(value["scalar_closure"]["imported_rows"]) == 3
    assert value["scalar_closure"]["newly_evaluated_row_count"] == 9


def test_all_companion_widths_are_below_gate() -> None:
    value = json.loads(CERTIFICATE.read_text())
    rows = value["scalar_closure"]["imported_rows"] + value["scalar_closure"]["newly_evaluated_rows"]
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in rows)


def test_same_index_only_mutation_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["same_index_only_mutation"]["omitted_required_row_count"] == 6
    assert value["same_index_only_mutation"]["detected"] is True


def test_deleted_companion_row_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["scalar_closure"]["newly_evaluated_rows"].pop()
    with pytest.raises(AssertionError):
        verify(value)
