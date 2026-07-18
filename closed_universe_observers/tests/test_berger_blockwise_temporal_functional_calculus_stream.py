import json
from fractions import Fraction
from math import factorial

import pytest

from closed_universe_observers.generate_berger_blockwise_temporal_functional_calculus_stream import CERTIFICATE, dressed_block
from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import CZERO
from closed_universe_observers.verify_berger_blockwise_temporal_functional_calculus_stream import verify


def test_extreme_scalar_block_microphase_dressing() -> None:
    moments = {power: [CZERO] for power in range(0, 29, 2)}
    one = ((Fraction(1), Fraction(1)), (Fraction(0), Fraction(0)))
    for power in moments:
        moments[power] = [one]
    spatial, temporal = dressed_block(138, Fraction(70), moments)
    eigenvalue = Fraction(196000, 9)
    expected = sum(Fraction((-1) ** n) * eigenvalue**n / factorial(2 * n) / 48 ** (2 * n) for n in range(15))
    assert spatial == [((expected, expected), (Fraction(0), Fraction(0)))]
    assert temporal == CZERO


def test_zero_input_stays_zero() -> None:
    moments = {power: [CZERO] for power in range(0, 29, 2)}
    spatial, temporal = dressed_block(0, Fraction(0), moments)
    assert all(value == CZERO for value in spatial)
    assert temporal == CZERO


@pytest.mark.parametrize(
    "field",
    (
        "populated_detector_column_charge_block_count",
        "spatial_microphase_dressed_amplitude_interval_count",
        "temporal_microphase_dressed_amplitude_interval_count",
    ),
)
def test_aggregate_count_mutation_is_rejected(field: str) -> None:
    value = json.loads(CERTIFICATE.read_text())
    value["coverage"][field] += 1
    with pytest.raises(AssertionError):
        verify(value)
