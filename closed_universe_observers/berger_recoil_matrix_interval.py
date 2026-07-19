"""Complex matrix/vector interval primitives for finite Berger Green stages."""

from __future__ import annotations

from fractions import Fraction
from math import factorial
from typing import Any, Mapping, Sequence

from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
)


Vector = Sequence[ComplexRationalInterval]
Matrix = Sequence[Sequence[ComplexRationalInterval]]


def _complex_from_serialized(value: Mapping[str, Mapping[str, str]]) -> ComplexRationalInterval:
    return ComplexRationalInterval(
        RationalInterval.from_serialized(value["real"]),
        RationalInterval.from_serialized(value["imaginary"]),
    )


def kernel_stage_from_sine_enclosure(
    enclosure: Mapping[str, Any], *, label: str | None = None
) -> dict[str, object]:
    """Convert a sparse ``enclose_exact_mode_sine_kernel`` result to a dense stage."""
    dimension = int(enclosure["dimension"])
    matrices = []
    for coefficient in enclosure["coefficient_matrices"]:
        matrix = [
            [ComplexRationalInterval.point() for _ in range(dimension)]
            for _ in range(dimension)
        ]
        for entry in coefficient["entries"]:
            matrix[int(entry["row"])][int(entry["column"])] = _complex_from_serialized(entry)
        matrices.append(matrix)
    return {
        "label": label or f"{enclosure['family']}_two_j{enclosure['two_j']}_degree{enclosure['form_degree']}",
        "coefficient_matrices": matrices,
        "uniform_remainder_upper": Fraction(enclosure["uniform_sine_kernel_remainder_upper"]),
    }


def _vector_add(left: Vector, right: Vector) -> list[ComplexRationalInterval]:
    return [a + b for a, b in zip(left, right)]


def _matrix_vector(matrix: Matrix, vector: Vector) -> list[ComplexRationalInterval]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), ComplexRationalInterval.point())
        for row in matrix
    ]


def _vector_norm_upper(vector: Vector) -> Fraction:
    return max((entry.absolute_upper() for entry in vector), default=Fraction(0))


def _matrix_norm_upper(matrix: Matrix) -> Fraction:
    return max(
        (sum((entry.absolute_upper() for entry in row), Fraction(0)) for row in matrix),
        default=Fraction(0),
    )


def _polynomial_vector_upper(coefficients: Sequence[Vector], length: Fraction) -> Fraction:
    return sum(
        (_vector_norm_upper(vector) * length**power for power, vector in enumerate(coefficients)),
        Fraction(0),
    )


def _polynomial_matrix_upper(coefficients: Sequence[Matrix], length: Fraction) -> Fraction:
    return sum(
        (_matrix_norm_upper(matrix) * length**power for power, matrix in enumerate(coefficients)),
        Fraction(0),
    )


def _validate_vector_polynomial(coefficients: Sequence[Vector]) -> int:
    if not coefficients or not coefficients[0]:
        raise ValueError("vector polynomial must be nonempty")
    dimension = len(coefficients[0])
    if any(len(vector) != dimension for vector in coefficients):
        raise ValueError("vector polynomial dimensions must agree")
    return dimension


def _validate_matrix_polynomial(coefficients: Sequence[Matrix], dimension: int) -> None:
    if not coefficients:
        raise ValueError("kernel matrix polynomial must be nonempty")
    if any(len(matrix) != dimension or any(len(row) != dimension for row in matrix) for matrix in coefficients):
        raise ValueError("kernel matrices must be square and match the vector dimension")


def multiply_vector_polynomial_by_real_interval(
    *,
    coefficients: Sequence[Vector],
    uniform_remainder_upper: Fraction,
    multiplier: RationalInterval,
) -> dict[str, object]:
    """Enclose pointwise multiplication by any real scalar in ``multiplier``."""
    _validate_vector_polynomial(coefficients)
    uniform_remainder_upper = Fraction(uniform_remainder_upper)
    if uniform_remainder_upper < 0:
        raise ValueError("uniform remainder must be nonnegative")
    complex_multiplier = ComplexRationalInterval(multiplier, RationalInterval.point(0))
    output = [[entry * complex_multiplier for entry in vector] for vector in coefficients]
    multiplier_upper = max(abs(multiplier.lower), abs(multiplier.upper))
    return {
        "polynomial_coefficients": [
            [entry.serialize() for entry in vector] for vector in output
        ],
        "uniform_remainder_upper": str(multiplier_upper * uniform_remainder_upper),
        "claim_boundary": "pointwise real cell-interval multiplication of a supplied complex vector polynomial",
    }


def evaluate_matrix_green_time_convolution_interval(
    *,
    source_coefficients: Sequence[Vector],
    source_remainder_upper: Fraction,
    kernel_stages: Sequence[Mapping[str, Any]],
    slab_length: Fraction,
    orientation: str,
) -> dict[str, object]:
    """Compose square matrix Green polynomials with a complex vector polynomial."""
    dimension = _validate_vector_polynomial(source_coefficients)
    slab_length = Fraction(slab_length)
    remainder = Fraction(source_remainder_upper)
    if slab_length <= 0:
        raise ValueError("slab_length must be positive")
    if remainder < 0:
        raise ValueError("source remainder must be nonnegative")
    if orientation not in ("retarded", "advanced"):
        raise ValueError("orientation must be retarded or advanced")
    if not kernel_stages:
        raise ValueError("at least one kernel stage is required")

    coefficients = [list(vector) for vector in source_coefficients]
    stage_rows = []
    for stage_index, stage in enumerate(kernel_stages):
        kernels = stage.get("coefficient_matrices", ())
        _validate_matrix_polynomial(kernels, dimension)
        kernel_remainder = Fraction(stage.get("uniform_remainder_upper", 0))
        if kernel_remainder < 0:
            raise ValueError("kernel remainder must be nonnegative")
        output = [
            [ComplexRationalInterval.point() for _ in range(dimension)]
            for _ in range(len(coefficients) + len(kernels))
        ]
        for source_power, source_vector in enumerate(coefficients):
            for kernel_power, kernel_matrix in enumerate(kernels):
                output_power = source_power + kernel_power + 1
                beta = Fraction(
                    factorial(source_power) * factorial(kernel_power),
                    factorial(output_power),
                )
                term = [entry.scale(beta) for entry in _matrix_vector(kernel_matrix, source_vector)]
                output[output_power] = _vector_add(output[output_power], term)
        source_upper = _polynomial_vector_upper(coefficients, slab_length)
        kernel_upper = _polynomial_matrix_upper(kernels, slab_length)
        output_remainder = slab_length * (
            source_upper * kernel_remainder
            + kernel_upper * remainder
            + remainder * kernel_remainder
        )
        stage_rows.append(
            {
                "stage": stage_index,
                "kernel_label": str(stage.get("label", f"stage_{stage_index}")),
                "uniform_remainder_upper": str(output_remainder),
            }
        )
        coefficients = output
        remainder = output_remainder

    return {
        "orientation": orientation,
        "causal_coordinate": "t-t_left" if orientation == "retarded" else "t_right-t",
        "dimension": dimension,
        "slab_length": str(slab_length),
        "stages": stage_rows,
        "polynomial_coefficients": [
            [entry.serialize() for entry in vector] for vector in coefficients
        ],
        "uniform_remainder_upper": str(remainder),
        "claim_boundary": "supplied finite-dimensional complex matrix/vector polynomial Green stages; no physical Berger form binding or I_abc evaluation",
    }
