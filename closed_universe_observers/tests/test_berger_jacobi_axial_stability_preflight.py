import json
from fractions import Fraction

import pytest

from closed_universe_observers.generate_berger_jacobi_axial_stability_preflight import (
    CERTIFICATE,
    jacobi_series_coefficient,
    raw_factored_coefficient,
)
from closed_universe_observers.verify_berger_jacobi_axial_stability_preflight import verify


def test_exact_jacobi_factorization_coefficients() -> None:
    for n in range(16):
        for r in range(n // 2 + 1):
            d = n - 2 * r
            for order in range(r + 1):
                assert jacobi_series_coefficient(r, d, order) == raw_factored_coefficient(r, d, order)


def test_axial_width_obstruction_is_strict() -> None:
    value = json.loads(CERTIFICATE.read_text())
    sentinels = {row["two_j"]: row for row in value["axial_sentinel_audits"]}
    assert Fraction(sentinels[974]["partial_interval_width_lower"]) < Fraction(1, 10)
    assert Fraction(sentinels[975]["partial_interval_width_lower"]) > Fraction(1, 10)
    assert Fraction(sentinels[2047]["partial_interval_width_lower"]) > 1000


def test_width_mutation_is_rejected() -> None:
    value = json.loads(CERTIFICATE.read_text())
    sentinel = next(row for row in value["axial_sentinel_audits"] if row["two_j"] == 975)
    sentinel["partial_interval_width_lower"] = "0.1"
    with pytest.raises(AssertionError):
        verify(value)
