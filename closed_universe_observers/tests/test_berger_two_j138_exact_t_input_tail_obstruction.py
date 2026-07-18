import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_two_j138_exact_t_input_tail_obstruction import (
    CERTIFICATE,
    _absolute_component_lower,
)
from closed_universe_observers.generate_berger_polarization_clebsch_gordan_recurrence import (
    axial_scalar_recurrence,
)
from closed_universe_observers.verify_berger_two_j138_exact_t_input_tail_obstruction import verify


def test_selected_recurrence_requires_first_upper_neighbor() -> None:
    terms = axial_scalar_recurrence(139, 69, 69, "y0")
    assert {row["next_two_j"] for row in terms} == {138, 140}


def test_cartesian_component_lower_bound() -> None:
    value = ((Fraction(4, 5), Fraction(9, 10)), (Fraction(-1, 10), Fraction(1, 10)))
    assert _absolute_component_lower(value) == Fraction(4, 5)


def test_spatial_lower_bound_mutation_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    value["cutoff_audit"]["witness"]["selected_spatial_absolute_lower"] = "4/5"
    with pytest.raises(AssertionError):
        verify(value)
