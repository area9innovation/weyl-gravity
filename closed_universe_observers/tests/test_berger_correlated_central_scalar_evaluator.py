import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_correlated_central_scalar_evaluator import (
    CERTIFICATE,
    legendre_coefficient,
)
from closed_universe_observers.verify_berger_correlated_central_scalar_evaluator import verify


def test_low_legendre_coefficients() -> None:
    assert [(-1) ** k * legendre_coefficient(2, k) for k in range(3)] == [1, -6, 6]


def test_all_certified_central_overlaps_pass() -> None:
    value = json.loads(CERTIFICATE.read_text())
    assert value["coverage"]["low_rail_overlap_count"] == 70
    assert value["coverage"]["low_rail_overlap_defect_count"] == 0


def test_two_j256_width_mutation_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    sentinel = {row["two_j"]: row for row in value["sentinel_audits"]}[256]
    sentinel["interval"]["width"] = "1/1000"
    with pytest.raises(AssertionError):
        verify(value)
