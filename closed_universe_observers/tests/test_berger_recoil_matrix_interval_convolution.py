from fractions import Fraction

import pytest

from closed_universe_observers.berger_recoil_interval_stream import ComplexRationalInterval, RationalInterval
from closed_universe_observers.berger_recoil_matrix_interval import (
    evaluate_matrix_green_time_convolution_interval,
    kernel_stage_from_sine_enclosure,
    multiply_vector_polynomial_by_real_interval,
)
from closed_universe_observers.generate_berger_recoil_matrix_interval_convolution import build


def _point(value):
    return ComplexRationalInterval.point(value)


def _identity(scale0=1, scale1=1):
    return [[_point(scale0), _point(0)], [_point(0), _point(scale1)]]


def test_two_matrix_volterra_stages_have_exact_beta_coefficients():
    value = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=[[_point(1), _point(2)]],
        source_remainder_upper=Fraction(0),
        kernel_stages=[
            {"label": "diagonal", "coefficient_matrices": [_identity(1, 2)]},
            {"label": "identity", "coefficient_matrices": [_identity()]},
        ],
        slab_length=Fraction(1),
        orientation="retarded",
    )
    assert value["polynomial_coefficients"][2][0]["real"]["lower"] == "1/2"
    assert value["polynomial_coefficients"][2][1]["real"]["lower"] == "2"
    assert value["uniform_remainder_upper"] == "0"


def test_complex_cell_multiplier_and_remainders_are_enclosed():
    multiplied = multiply_vector_polynomial_by_real_interval(
        coefficients=[[ComplexRationalInterval.point(1, 1)]],
        uniform_remainder_upper=Fraction(1, 10),
        multiplier=RationalInterval(Fraction(-1), Fraction(2)),
    )
    assert multiplied["polynomial_coefficients"][0][0]["real"]["lower"] == "-1"
    assert multiplied["polynomial_coefficients"][0][0]["imaginary"]["upper"] == "2"
    assert multiplied["uniform_remainder_upper"] == "1/5"
    convolved = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=[[_point(1), _point(2)]],
        source_remainder_upper=Fraction(1, 10),
        kernel_stages=[{
            "coefficient_matrices": [_identity(1, 2)],
            "uniform_remainder_upper": Fraction(1, 20),
        }],
        slab_length=Fraction(1),
        orientation="advanced",
    )
    assert convolved["uniform_remainder_upper"] == "61/200"


def test_dimensions_and_orientations_fail_closed():
    with pytest.raises(ValueError, match="match the vector dimension"):
        evaluate_matrix_green_time_convolution_interval(
            source_coefficients=[[_point(1), _point(2)]],
            source_remainder_upper=0,
            kernel_stages=[{"coefficient_matrices": [[[_point(1)]]]}],
            slab_length=1,
            orientation="retarded",
        )
    with pytest.raises(ValueError, match="orientation"):
        evaluate_matrix_green_time_convolution_interval(
            source_coefficients=[[_point(1)]], source_remainder_upper=0,
            kernel_stages=[{"coefficient_matrices": [[[_point(1)]]]}],
            slab_length=1, orientation="acausal",
        )


def test_sparse_finite_kernel_serialization_adapts_to_dense_stage():
    enclosure = {
        "dimension": 2, "family": "Maxwell", "two_j": 0, "form_degree": 1,
        "uniform_sine_kernel_remainder_upper": "1/100",
        "coefficient_matrices": [{"entries": [
            {"row": 0, "column": 0, "real": {"lower": "1", "upper": "1"}, "imaginary": {"lower": "0", "upper": "0"}},
            {"row": 1, "column": 1, "real": {"lower": "2", "upper": "2"}, "imaginary": {"lower": "0", "upper": "0"}},
        ]}],
    }
    stage = kernel_stage_from_sine_enclosure(enclosure)
    assert stage["coefficient_matrices"][0][0][0] == _point(1)
    assert stage["coefficient_matrices"][0][0][1] == _point(0)
    assert stage["uniform_remainder_upper"] == Fraction(1, 100)


def test_certificate_does_not_promote_physical_binding():
    value = build()
    assert value["flags"]["COMPLEX_MATRIX_VECTOR_INTERVAL_CONVOLUTION_EXPORTED"] is True
    assert value["flags"]["FINITE_MODE_KERNEL_ENCLOSURE_ADAPTER_EXPORTED"] is True
    assert value["flags"]["PHYSICAL_BERGER_FORM_CHAIN_BOUND"] is False
