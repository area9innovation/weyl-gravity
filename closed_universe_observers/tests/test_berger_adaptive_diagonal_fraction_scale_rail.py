import copy
from fractions import Fraction
import json

import pytest

from closed_universe_observers.generate_berger_adaptive_diagonal_fraction_scale_rail import CERTIFICATE
from closed_universe_observers.verify_berger_adaptive_diagonal_fraction_scale_rail import verify


def test_adaptive_scale_rows_are_below_gate() -> None:
    value = json.loads(CERTIFICATE.read_text())
    rows = value["even_scale_rows"] + value["odd_scale_rows"]
    assert len(rows) == 6
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in rows)


def test_refinement_is_radial_only_at_three_eighths() -> None:
    value = json.loads(CERTIFICATE.read_text())
    rows = value["even_scale_rows"] + value["odd_scale_rows"]
    refined = [row for row in rows if row["declared_even_index_fraction"] == "3/8"]
    assert all(row["radial_subdivisions"] == 128 for row in refined)
    assert all(row["angular_subdivisions"] == 64 for row in refined)
    mutation = value["anisotropic_resolution_mutation"]
    assert Fraction(mutation["interval"]["width"]) > Fraction(1, 10)


def test_angular_only_mutation_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["anisotropic_resolution_mutation"]["interval"]["width"] = "1/10"
    with pytest.raises(AssertionError):
        verify(value)


def test_complete_rail_claim_remains_false() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["flags"]["COMPLETE_DIAGONAL_STREAM_EXPORTED"] is False
    assert value["flags"]["ALL_CLOCK_POWERS_AND_POLARIZED_ROWS_EVALUATED"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False
