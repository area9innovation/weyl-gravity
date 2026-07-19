"""Bind finite detector polynomials to the exact Berger spacetime ``Dhat_1``."""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from math import factorial
from typing import Any, Mapping, Sequence

import sympy as sp

from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
    _sympy_complex_interval,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import d_matrix


Vector = Sequence[ComplexRationalInterval]
Matrix = Sequence[Sequence[ComplexRationalInterval]]


def _zero_vector(dimension: int) -> list[ComplexRationalInterval]:
    return [ComplexRationalInterval.point() for _ in range(dimension)]


def _serialized_complex(value: Mapping[str, Mapping[str, str]]) -> ComplexRationalInterval:
    return ComplexRationalInterval(
        RationalInterval.from_serialized(value["real"]),
        RationalInterval.from_serialized(value["imag"]),
    )


def _matrix_vector(matrix: Matrix, vector: Vector) -> list[ComplexRationalInterval]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), ComplexRationalInterval.point())
        for row in matrix
    ]


def _vector_add(left: Vector, right: Vector) -> list[ComplexRationalInterval]:
    return [a + b for a, b in zip(left, right)]


def _interval_matrix(matrix: sp.Matrix, radical_bits: int) -> list[list[ComplexRationalInterval]]:
    if radical_bits < 8:
        raise ValueError("radical_bits must be at least 8")
    zero_mass = RationalInterval.point(0)
    return [
        [
            _sympy_complex_interval(
                sp.sstr(matrix[row, column]),
                mass_squared_interval=zero_mass,
                radical_bits=radical_bits,
            )
            for column in range(matrix.cols)
        ]
        for row in range(matrix.rows)
    ]


@lru_cache(maxsize=None)
def _cached_interval_d_matrix(
    two_j: int, degree: int, radical_bits: int
) -> tuple[tuple[ComplexRationalInterval, ...], ...]:
    """Content-stable exact de Rham interval matrix cached by mode scope."""
    return tuple(
        tuple(row)
        for row in _interval_matrix(d_matrix(two_j, degree), radical_bits)
    )


def _matrix_norm_upper(matrix: Matrix) -> Fraction:
    return max(
        (sum((entry.absolute_upper() for entry in row), Fraction(0)) for row in matrix),
        default=Fraction(0),
    )


def _detector_mode(
    certificate: Mapping[str, Any], detector: str, two_j: int
) -> Mapping[str, Any]:
    if certificate.get("result_id") != "BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE":
        raise ValueError("wrong detector polynomial certificate")
    if certificate.get("flags", {}).get("FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED") is not True:
        raise ValueError("finite advanced-Maxwell detector image is not certified")
    if detector not in ("D0", "D1"):
        raise ValueError("detector must be D0 or D1")
    extended_two_j5 = all(
        certificate.get("flags", {}).get(flag) is True
        for flag in (
            "DIRECT_DETECTOR_POLYNOMIAL_PROVIDER_TWO_J5_EXPORTED",
            "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
        )
    )
    maximum_two_j = 5 if extended_two_j5 else 4
    if not 0 <= two_j <= maximum_two_j:
        raise ValueError(
            f"detector form binding covers only 0<=two_j<={maximum_two_j}"
        )
    detector_row = next(
        (row for row in certificate["detectors"] if row["detector_id"] == detector),
        None,
    )
    if detector_row is None:
        raise ValueError("selected detector is absent")
    mode = next((row for row in detector_row["modes"] if row["two_j"] == two_j), None)
    if mode is None:
        raise ValueError("selected finite mode is absent")
    if int(mode["dimension"]) != two_j + 1:
        raise ValueError("detector representation dimension drifted")
    return mode


def _assemble(
    certificate: Mapping[str, Any], *, detector: str, two_j: int, column: int
) -> tuple[list[list[ComplexRationalInterval]], Mapping[str, Any]]:
    mode = _detector_mode(certificate, detector, two_j)
    n = two_j + 1
    if not 0 <= column < n:
        raise ValueError("column must lie in the selected representation")
    blocks = (
        "temporal_scalar_advanced_polynomial",
        "spatial_one_form_advanced_polynomial",
    )
    powers = [
        int(coefficient["T_power"])
        for block in blocks
        for entry in mode[block]
        if int(entry["column"]) == column
        for coefficient in entry["coefficients"]
    ]
    maximum_power = max(powers, default=0)
    coefficients = [_zero_vector(4 * n) for _ in range(maximum_power + 1)]
    occupied: set[tuple[int, int]] = set()
    for block in blocks:
        for entry in mode[block]:
            if int(entry["column"]) != column:
                continue
            row = int(entry["row"])
            if not 0 <= row < n:
                raise ValueError("detector row lies outside the representation")
            if block.startswith("temporal"):
                output = row
            else:
                component = int(entry["coframe_component"])
                if component not in (1, 2, 3):
                    raise ValueError("invalid spatial coframe component")
                output = n + (component - 1) * n + row
            for coefficient in entry["coefficients"]:
                power = int(coefficient["T_power"])
                if power < 0 or (power, output) in occupied:
                    raise ValueError("duplicate or negative detector polynomial coordinate")
                occupied.add((power, output))
                coefficients[power][output] = _serialized_complex(coefficient)
    return coefficients, mode["uniform_entire_series_remainders"]


def assemble_detector_advanced_maxwell_polynomial(
    certificate: Mapping[str, Any], *, detector: str, two_j: int, column: int
) -> dict[str, object]:
    """Assemble one passive-column advanced Maxwell one-form polynomial."""
    coefficients, remainder = _assemble(
        certificate, detector=detector, two_j=two_j, column=column
    )
    spatial = Fraction(remainder["spatial_cosine_entry_remainder_upper"])
    temporal = Fraction(remainder["temporal_sine_entry_remainder_upper"])
    return {
        "detector": detector,
        "two_j": two_j,
        "column": column,
        "dimension": len(coefficients[0]),
        "basis_order": "[temporal scalar rows; theta1 rows; theta2 rows; theta3 rows]",
        "coefficient_variable": "T=t_detector_center-t",
        "polynomial_coefficients": [
            [entry.serialize() for entry in vector] for vector in coefficients
        ],
        "block_remainder_uppers": {
            "temporal_scalar": str(temporal),
            "spatial_one_form": str(spatial),
        },
        "uniform_vector_remainder_upper": str(max(spatial, temporal)),
        "claim_boundary": "finite advanced-Maxwell one-form through two_j=4; no spacetime derivative, massive image or recoil scalar",
    }


def _cosine_time_derivative_tail(
    *, operator_norm: Fraction, tau_max: Fraction, series_order: int
) -> Fraction:
    """Bound d/dtau of the omitted cosine series in the induced infinity norm."""
    if operator_norm < 0 or tau_max <= 0 or series_order < 0:
        raise ValueError("invalid derivative-tail inputs")
    if operator_norm == 0:
        return Fraction(0)
    ratio = operator_norm * tau_max**2 / Fraction(
        (2 * series_order + 2) * (2 * series_order + 3)
    )
    if ratio >= 1:
        raise ValueError("time-derivative tail majorant is not contractive")
    first = (
        operator_norm ** (series_order + 1)
        * tau_max ** (2 * series_order + 1)
        / factorial(2 * series_order + 1)
    )
    return first / (1 - ratio)


def _apply_spacetime_dhat1(
    certificate: Mapping[str, Any],
    *,
    detector: str,
    two_j: int,
    column: int,
    radical_bits: int,
    time_derivative_sign: int,
) -> dict[str, object]:
    if time_derivative_sign not in (-1, 1):
        raise ValueError("time_derivative_sign must be -1 or 1")
    coefficients, remainder = _assemble(
        certificate, detector=detector, two_j=two_j, column=column
    )
    n = two_j + 1
    d0 = _cached_interval_d_matrix(two_j, 0, radical_bits)
    d1 = _cached_interval_d_matrix(two_j, 1, radical_bits)
    output: list[list[ComplexRationalInterval]] = []
    for power, vector in enumerate(coefficients):
        alpha = vector[:n]
        beta = vector[n:]
        top = [-entry for entry in _matrix_vector(d0, alpha)]
        if power + 1 < len(coefficients):
            derivative = [
                entry.scale(time_derivative_sign * (power + 1))
                for entry in coefficients[power + 1][n:]
            ]
            top = _vector_add(top, derivative)
        bottom = _matrix_vector(d1, beta)
        output.append(top + bottom)

    order = int(certificate["series_convention"]["order"])
    tau_max = Fraction(remainder["tau_max"])
    lambda1 = Fraction(remainder["Delta1_infinity_norm_upper"])
    derivative_remainder = _cosine_time_derivative_tail(
        operator_norm=lambda1, tau_max=tau_max, series_order=order
    )
    spatial_remainder = Fraction(remainder["spatial_cosine_entry_remainder_upper"])
    temporal_remainder = Fraction(remainder["temporal_sine_entry_remainder_upper"])
    d0_norm = _matrix_norm_upper(d0)
    d1_norm = _matrix_norm_upper(d1)
    temporal_spatial_one_form = derivative_remainder + d0_norm * temporal_remainder
    spatial_two_form = d1_norm * spatial_remainder
    return {
        "detector": detector,
        "two_j": two_j,
        "column": column,
        "input_dimension": 4 * n,
        "output_dimension": 6 * n,
        "operator": "Dhat_1(alpha,beta)=(partial_t beta-dSigma alpha,dSigma beta)",
        "input_basis_order": "[temporal scalar rows; theta1 rows; theta2 rows; theta3 rows]",
        "output_basis_order": "[dt-wedge theta1 rows; dt-wedge theta2 rows; dt-wedge theta3 rows; theta1-wedge-theta2 rows; theta1-wedge-theta3 rows; theta2-wedge-theta3 rows]",
        "coefficient_variable": "T=t_detector_center-t",
        "physical_time_derivative": "partial_t=-partial_T",
        "polynomial_coefficients": [
            [entry.serialize() for entry in vector] for vector in output
        ],
        "remainder_audit": {
            "series_order": order,
            "tau_max": str(tau_max),
            "Delta1_infinity_norm_upper": str(lambda1),
            "d0_interval_infinity_norm_upper": str(d0_norm),
            "d1_interval_infinity_norm_upper": str(d1_norm),
            "spatial_cosine_time_derivative_remainder_upper": str(derivative_remainder),
            "temporal_spatial_one_form_remainder_upper": str(temporal_spatial_one_form),
            "spatial_two_form_remainder_upper": str(spatial_two_form),
            "uniform_output_vector_remainder_upper": str(
                max(temporal_spatial_one_form, spatial_two_form)
            ),
        },
        "claim_boundary": "finite detector-selected Dhat_1 advanced-Maxwell two-form through two_j=4; massive Green image, Cauchy trace and I_abc remain open",
    }


def apply_spacetime_dhat1_to_detector_advanced_maxwell(
    certificate: Mapping[str, Any],
    *,
    detector: str,
    two_j: int,
    column: int,
    radical_bits: int = 80,
) -> dict[str, object]:
    """Apply the exact Berger ``Dhat_1`` with ``partial_t=-partial_T``."""
    return _apply_spacetime_dhat1(
        certificate,
        detector=detector,
        two_j=two_j,
        column=column,
        radical_bits=radical_bits,
        time_derivative_sign=-1,
    )
