import copy
from fractions import Fraction
import json

import pytest
from jsonschema import ValidationError

from closed_universe_observers.generate_berger_correlated_diagonal_fraction_stream import CERTIFICATE
from closed_universe_observers.verify_berger_correlated_diagonal_fraction_stream import verify


def test_declared_even_odd_fraction_rows_are_narrow() -> None:
    value = json.loads(CERTIFICATE.read_text())
    rows = value["even_fraction_rows"] + value["odd_companion_rows"]
    assert len(rows) == 6
    assert {row["declared_even_index_fraction"] for row in rows} == {"1/8", "1/4", "3/8"}
    assert all(Fraction(row["interval"]["width"]) < Fraction(1, 10) for row in rows)


def test_sobolev_route_remains_fail_closed() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["sobolev_tail_preflight"]["route_status"] == "OPEN"
    assert value["sobolev_tail_preflight"]["evaluated_sobolev_norm"] is False
    assert value["flags"]["VALIDATED_INFINITE_MODE_TAIL_UPPER_BOUND_EXPORTED"] is False


def test_missing_odd_companion_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["odd_companion_rows"].pop()
    with pytest.raises(ValidationError):
        verify(value)


def test_width_boundary_is_rejected() -> None:
    value = copy.deepcopy(json.loads(CERTIFICATE.read_text()))
    value["even_fraction_rows"][0]["interval"]["width"] = "1/10"
    with pytest.raises(AssertionError):
        verify(value)
