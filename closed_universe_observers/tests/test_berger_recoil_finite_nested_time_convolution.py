from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    evaluate_nested_green_time_convolution_interval,
)
from closed_universe_observers.generate_berger_recoil_finite_nested_time_convolution import build


def _point(value):
    return RationalInterval.point(value)


def test_two_stage_exact_beta_convolution():
    value = evaluate_nested_green_time_convolution_interval(
        source_coefficients=[_point(1), _point(1)], source_remainder_upper=Fraction(0),
        kernel_stages=[
            {"coefficients": [_point(2)], "uniform_remainder_upper": Fraction(0)},
            {"coefficients": [_point(0), _point(1)], "uniform_remainder_upper": Fraction(0)},
        ],
        slab_length=Fraction(1), orientation="retarded",
    )
    assert [row["lower"] for row in value["polynomial_coefficients"]] == ["0", "0", "0", "1/3", "1/12"]
    assert value["uniform_remainder_upper"] == "0"


def test_advanced_orientation_uses_reverse_causal_coordinate():
    value = evaluate_nested_green_time_convolution_interval(
        source_coefficients=[_point(1)], source_remainder_upper=Fraction(0),
        kernel_stages=[{"coefficients": [_point(1)]}],
        slab_length=Fraction(2), orientation="advanced",
    )
    assert value["causal_coordinate"] == "t_right-t"
    assert value["polynomial_coefficients"][1]["lower"] == "1"


def test_uniform_remainders_are_propagated_rationally():
    value = evaluate_nested_green_time_convolution_interval(
        source_coefficients=[_point(1), _point(1)], source_remainder_upper=Fraction(1, 10),
        kernel_stages=[{"coefficients": [_point(2)], "uniform_remainder_upper": Fraction(1, 20)}],
        slab_length=Fraction(1), orientation="retarded",
    )
    assert value["uniform_remainder_upper"] == "61/200"


def test_empty_kernel_chain_is_rejected_and_complete_binding_stays_open():
    with pytest.raises(ValueError, match="at least one"):
        evaluate_nested_green_time_convolution_interval(
            source_coefficients=[_point(1)], source_remainder_upper=Fraction(0),
            kernel_stages=[], slab_length=Fraction(1), orientation="retarded",
        )
    value = build()
    assert value["flags"]["FINITE_POLYNOMIAL_NESTED_TIME_CONVOLUTION_EXPORTED"] is True
    assert value["flags"]["COMPLETE_PHYSICAL_NESTED_TIME_CONVOLUTION_BACKEND_EXPORTED"] is False
