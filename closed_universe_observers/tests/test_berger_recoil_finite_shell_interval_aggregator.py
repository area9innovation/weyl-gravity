from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval, evaluate_recoil_shell_interval
from closed_universe_observers.generate_berger_recoil_finite_shell_interval_aggregator import (
    build,
    fixture,
    missing_passive_column_mutation_detected,
)


def test_signed_exact_fixture_and_certified_formula():
    value = build()
    assert value["exact_fixture"]["shell_interval"] == {"lower": "-16", "upper": "-72/5", "width": "8/5"}
    assert "g_b sum_c g_c^2" in value["callable_contract"]["formula"]


def test_interval_multiplication_encloses_all_endpoint_products():
    result = RationalInterval(Fraction(-2), Fraction(3)) * RationalInterval(Fraction(-5), Fraction(7))
    assert result == RationalInterval(Fraction(-15), Fraction(21))


def test_missing_passive_column_is_rejected():
    assert missing_passive_column_mutation_detected() is True
    with pytest.raises(ValueError, match=r"two_j\+1 passive columns"):
        evaluate_recoil_shell_interval(
            two_j=1,
            detector=0,
            source_preparation=0,
            source_coupling=Fraction(1),
            feedback_couplings={0: Fraction(1), 1: Fraction(1)},
            inverse_berger_volume=RationalInterval.point(1),
            channel_columns={0: [RationalInterval.point(1)], 1: [RationalInterval.point(1)]},
        )


def test_weight_and_source_coupling_mutations_change_result():
    canonical = fixture()["shell_interval"]
    assert fixture(omit_weight=True)["shell_interval"] != canonical
    assert fixture(square_source_coupling=True)["shell_interval"] != canonical
