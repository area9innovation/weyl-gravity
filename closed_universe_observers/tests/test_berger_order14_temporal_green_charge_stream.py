import json
from fractions import Fraction
from math import factorial

import pytest

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import CZERO
from closed_universe_observers.generate_berger_order14_temporal_green_charge_stream import (
    CERTIFICATE,
    _cosine_polynomial,
    block_polynomials,
    remainder_audits,
)
from closed_universe_observers.verify_berger_order14_temporal_green_charge_stream import verify


def test_scalar_extreme_charge_block_polynomial() -> None:
    moments = {power: [CZERO] for power in range(0, 29, 2)}
    moments[0] = [((Fraction(1), Fraction(1)), (Fraction(0), Fraction(0)))]
    spatial, temporal = block_polynomials(138, Fraction(70), moments)
    eigenvalue = Fraction(196000, 9)
    for index in (0, 1, 7, 14):
        expected = Fraction((-1) ** (index + 1)) * eigenvalue**index / factorial(2 * index)
        assert spatial[2 * index][0] == ((expected, expected), (Fraction(0), Fraction(0)))
    assert not temporal


def test_order14_extreme_witness_is_not_a_green_approximation() -> None:
    witness = _cosine_polynomial(Fraction(153125, 162))
    assert abs(witness) - 1 > 10**11
    audits = remainder_audits()
    assert [row["uniform_remainders_below_one"] for row in audits] == [False, False]
    assert all(Fraction(row["cosine_geometric_ratio"]) < 1 for row in audits)
    assert all(Fraction(row["sine_geometric_ratio"]) < 1 for row in audits)


def test_deleting_extreme_block_obstruction_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    value["remainder_audits"][1]["exact_cosine_error_absolute_lower"] = "0"
    with pytest.raises(AssertionError):
        verify(value)
