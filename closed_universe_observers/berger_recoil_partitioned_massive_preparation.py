"""Cell-partitioned finite massive preparation with rigorous endpoint bounds."""

from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import Any, Mapping, Sequence

from closed_universe_observers.berger_recoil_detector_form_binding import (
    _interval_matrix,
    apply_spacetime_dhat1_to_detector_advanced_maxwell,
)
from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
    enclose_exact_mode_sine_kernel,
)
from closed_universe_observers.berger_recoil_massive_diagonal_preparation import (
    _add,
    _adjoint,
    _block_diagonal_kernel_stage,
    _complex_from_serialized,
    _cosine_stage_from_sine_stage,
    _deserialize_polynomial,
    _detector_center_physical_time,
    _matrix_vector,
    _scale_real_interval,
    _switch_support,
    _translate_vector_polynomial,
)
from closed_universe_observers.berger_recoil_matrix_interval import (
    kernel_stage_from_sine_enclosure,
)
from closed_universe_observers.berger_recoil_switch_intervals import (
    emitter_switch_interval,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    d_matrix,
)


Vector = Sequence[ComplexRationalInterval]
Matrix = Sequence[Sequence[ComplexRationalInterval]]


def _vector_norm_upper(vector: Vector) -> Fraction:
    return max((entry.absolute_upper() for entry in vector), default=Fraction(0))


def _matrix_norm_upper(matrix: Matrix) -> Fraction:
    return max(
        (
            sum((entry.absolute_upper() for entry in row), Fraction(0))
            for row in matrix
        ),
        default=Fraction(0),
    )


def _add_box_error(
    vector: Vector, remainder: Fraction
) -> list[ComplexRationalInterval]:
    error = RationalInterval(-remainder, remainder)
    return [
        ComplexRationalInterval(entry.real + error, entry.imaginary + error)
        for entry in vector
    ]


def _real_interval_absolute_lower(interval: RationalInterval) -> Fraction:
    if interval.lower <= 0 <= interval.upper:
        return Fraction(0)
    return min(abs(interval.lower), abs(interval.upper))


def _vector_norm_squared_lower(vector: Vector) -> Fraction:
    return sum(
        (
            _real_interval_absolute_lower(entry.real) ** 2
            + _real_interval_absolute_lower(entry.imaginary) ** 2
            for entry in vector
        ),
        Fraction(0),
    )


def evaluate_partitioned_matrix_green_endpoint(
    *,
    source_coefficients: Sequence[Vector],
    source_remainder_upper: Fraction,
    kernel_stage: Mapping[str, Any],
    slab_length: Fraction,
    cells: Sequence[tuple[Fraction, Fraction, RationalInterval]],
) -> dict[str, object]:
    """Enclose ``integral K(L-y) h(y) f(y) dy`` over declared cells."""
    if not source_coefficients or not source_coefficients[0]:
        raise ValueError("source polynomial must be nonempty")
    dimension = len(source_coefficients[0])
    if any(len(vector) != dimension for vector in source_coefficients):
        raise ValueError("source polynomial dimensions must agree")
    kernels = kernel_stage["coefficient_matrices"]
    if not kernels or any(
        len(matrix) != dimension
        or any(len(row) != dimension for row in matrix)
        for matrix in kernels
    ):
        raise ValueError("kernel matrices must match the source dimension")
    slab_length = Fraction(slab_length)
    source_remainder_upper = Fraction(source_remainder_upper)
    kernel_remainder = Fraction(kernel_stage["uniform_remainder_upper"])
    if slab_length <= 0 or source_remainder_upper < 0 or kernel_remainder < 0:
        raise ValueError("invalid slab or remainder")
    if not cells or cells[0][0] != 0 or cells[-1][1] != slab_length:
        raise ValueError("cells must cover the full causal coordinate interval")
    if any(
        lower >= upper
        or (index and lower != cells[index - 1][1])
        for index, (lower, upper, _) in enumerate(cells)
    ):
        raise ValueError("cells must be ordered, nonempty and contiguous")

    output = [ComplexRationalInterval.point() for _ in range(dimension)]
    remainder = Fraction(0)
    cell_rows = []
    maximum_moment_power = len(source_coefficients) + len(kernels) - 2
    weighted_moments = [
        RationalInterval.point(0) for _ in range(maximum_moment_power + 1)
    ]
    for lower, upper, multiplier in cells:
        for power in range(maximum_moment_power + 1):
            moment = (
                upper ** (power + 1) - lower ** (power + 1)
            ) / Fraction(power + 1)
            weighted_moments[power] = weighted_moments[power] + multiplier.scale(
                moment
            )

        multiplier_upper = max(abs(multiplier.lower), abs(multiplier.upper))
        source_polynomial_upper = sum(
            (
                _vector_norm_upper(vector)
                * multiplier_upper
                * upper**power
                for power, vector in enumerate(source_coefficients)
            ),
            Fraction(0),
        )
        source_cell_remainder = multiplier_upper * source_remainder_upper
        maximum_kernel_argument = slab_length - lower
        kernel_polynomial_upper = sum(
            (
                _matrix_norm_upper(matrix) * maximum_kernel_argument**power
                for power, matrix in enumerate(kernels)
            ),
            Fraction(0),
        )
        cell_remainder = (upper - lower) * (
            source_polynomial_upper * kernel_remainder
            + kernel_polynomial_upper * source_cell_remainder
            + source_cell_remainder * kernel_remainder
        )
        remainder += cell_remainder
        cell_rows.append(
            {
                "causal_coordinate_interval": [str(lower), str(upper)],
                "multiplier": multiplier.serialize(),
                "uniform_remainder_upper": str(cell_remainder),
            }
        )
    for source_power, source_vector in enumerate(source_coefficients):
        for kernel_power, kernel_matrix in enumerate(kernels):
            base = _matrix_vector(kernel_matrix, source_vector)
            for expansion_power in range(kernel_power + 1):
                total_power = source_power + expansion_power
                exact_scalar = (
                    Fraction(comb(kernel_power, expansion_power))
                    * slab_length ** (kernel_power - expansion_power)
                    * (-1) ** expansion_power
                )
                multiplier = ComplexRationalInterval(
                    weighted_moments[total_power].scale(exact_scalar),
                    RationalInterval.point(0),
                )
                term = [entry * multiplier for entry in base]
                output = [a + b for a, b in zip(output, term)]
    return {
        "dimension": dimension,
        "slab_length": str(slab_length),
        "kernel_label": kernel_stage.get("label", "unnamed"),
        "cell_count": len(cells),
        "cells": cell_rows,
        "endpoint_vector_without_box_remainder": [
            entry.serialize() for entry in output
        ],
        "uniform_remainder_upper": str(remainder),
        "endpoint_vector": [
            entry.serialize() for entry in _add_box_error(output, remainder)
        ],
        "claim_boundary": "one supplied cell-partitioned matrix Green endpoint integral with a scalar multiplier hull on each cell",
    }


def evaluate_partitioned_positive_energy_preparation_at_support_left(
    *,
    detector_image_certificate: Mapping[str, Any],
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    moment_certificate: Mapping[str, Any],
    exact_kernel_certificate: Mapping[str, Any],
    detector: str,
    two_j: int,
    column: int,
    mass_squared_interval: RationalInterval,
    partition_count: int,
    radical_bits: int = 80,
) -> dict[str, object]:
    """Refine the finite preparation by retaining the positive switch cellwise."""
    if detector not in ("D0", "D1"):
        raise ValueError("detector must be D0 or D1")
    if mass_squared_interval.lower <= 0:
        raise ValueError("positive mass squared is required")
    if partition_count < 2 or partition_count % 2:
        raise ValueError("partition_count must be an even integer at least two")
    switch_id = {"D0": "h_0", "D1": "h_1"}[detector]
    support_left, support_right = _switch_support(switch_certificate, switch_id)
    slab_length = support_right - support_left
    center = _detector_center_physical_time(detector_profile_certificate, detector)
    shift = center - support_right

    dhat = apply_spacetime_dhat1_to_detector_advanced_maxwell(
        detector_image_certificate,
        detector=detector,
        two_j=two_j,
        column=column,
        radical_bits=radical_bits,
    )
    source_in_y = _translate_vector_polynomial(
        _deserialize_polynomial(dhat["polynomial_coefficients"]), shift
    )
    source_remainder = Fraction(
        dhat["remainder_audit"]["uniform_output_vector_remainder_upper"]
    )
    enclosures = {
        degree: enclose_exact_mode_sine_kernel(
            exact_kernel_certificate,
            two_j=two_j,
            family="massive_two_form",
            form_degree=degree,
            mass_squared_interval=mass_squared_interval,
            slab_length=slab_length,
            radical_bits=radical_bits,
        )
        for degree in (1, 2)
    }
    sine_components = {
        degree: kernel_stage_from_sine_enclosure(enclosures[degree])
        for degree in (1, 2)
    }
    cosine_components = {
        degree: _cosine_stage_from_sine_stage(
            sine_components[degree], enclosures[degree]
        )
        for degree in (1, 2)
    }
    sine_stage = _block_diagonal_kernel_stage(
        sine_components[1], sine_components[2]
    )
    cosine_stage = _block_diagonal_kernel_stage(
        cosine_components[1], cosine_components[2]
    )
    width = slab_length / partition_count
    cells = []
    for index in range(partition_count):
        y_lower = width * index
        y_upper = width * (index + 1)
        physical_cell = RationalInterval(
            support_right - y_upper, support_right - y_lower
        )
        switch = emitter_switch_interval(
            switch_certificate,
            moment_certificate,
            switch_id=switch_id,
            physical_time_interval=physical_cell,
        )
        cells.append(
            (
                y_lower,
                y_upper,
                RationalInterval.from_serialized(switch["value"]),
            )
        )
    diagonal_value = evaluate_partitioned_matrix_green_endpoint(
        source_coefficients=source_in_y,
        source_remainder_upper=source_remainder,
        kernel_stage=sine_stage,
        slab_length=slab_length,
        cells=cells,
    )
    diagonal_cosine = evaluate_partitioned_matrix_green_endpoint(
        source_coefficients=source_in_y,
        source_remainder_upper=source_remainder,
        kernel_stage=cosine_stage,
        slab_length=slab_length,
        cells=cells,
    )
    value = [
        _complex_from_serialized(entry)
        for entry in diagonal_value["endpoint_vector"]
    ]
    time_derivative = [
        -_complex_from_serialized(entry)
        for entry in diagonal_cosine["endpoint_vector"]
    ]

    operator = [
        [entry.scale(-6) for entry in row]
        for row in sine_stage["coefficient_matrices"][3]
    ]
    second_time_derivative = [-entry for entry in _matrix_vector(operator, value)]
    third_time_derivative = [
        -entry for entry in _matrix_vector(operator, time_derivative)
    ]
    n = two_j + 1
    d0 = _interval_matrix(d_matrix(two_j, 0), radical_bits)
    d1 = _interval_matrix(d_matrix(two_j, 1), radical_bits)
    d0_adj, d1_adj = _adjoint(d0), _adjoint(d1)
    alpha, beta = value[: 3 * n], value[3 * n :]
    alpha_t, beta_t = time_derivative[: 3 * n], time_derivative[3 * n :]
    alpha_tt, beta_tt = second_time_derivative[: 3 * n], second_time_derivative[3 * n :]
    alpha_ttt = third_time_derivative[: 3 * n]
    correction_top = _add(
        alpha_tt,
        _matrix_vector(d1_adj, beta_t),
        _matrix_vector(d0, _matrix_vector(d0_adj, alpha)),
    )
    correction_bottom = _add(
        _matrix_vector(d1, alpha_t),
        _matrix_vector(d1, _matrix_vector(d1_adj, beta)),
    )
    correction_t_top = _add(
        alpha_ttt,
        _matrix_vector(d1_adj, beta_tt),
        _matrix_vector(d0, _matrix_vector(d0_adj, alpha_t)),
    )
    correction_t_bottom = _add(
        _matrix_vector(d1, alpha_tt),
        _matrix_vector(d1, _matrix_vector(d1_adj, beta_t)),
    )
    inverse_mass = RationalInterval(
        Fraction(1) / mass_squared_interval.upper,
        Fraction(1) / mass_squared_interval.lower,
    )
    physical_value = _add(
        value,
        _scale_real_interval(correction_top + correction_bottom, inverse_mass),
    )
    physical_time_derivative = _add(
        time_derivative,
        _scale_real_interval(
            correction_t_top + correction_t_bottom, inverse_mass
        ),
    )

    alpha, beta = physical_value[: 3 * n], physical_value[3 * n :]
    beta_t = physical_time_derivative[3 * n :]
    covector_q = beta
    covector_p = _add(beta_t, [-entry for entry in _matrix_vector(d1, alpha)])
    d_delta_p = _matrix_vector(d1, _matrix_vector(d1_adj, covector_p))
    a_p = _add(covector_p, _scale_real_interval(d_delta_p, inverse_mass))
    d2 = _interval_matrix(d_matrix(two_j, 2), radical_bits)
    d2_adj = _adjoint(d2)
    delta_d_q = _matrix_vector(d2_adj, _matrix_vector(d2, covector_q))
    preparation_q = [-entry for entry in a_p]
    preparation_p = _add(
        delta_d_q, _scale_real_interval(covector_q, mass_squared_interval)
    )
    covector_q_norm_squared_lower = _vector_norm_squared_lower(covector_q)
    covector_p_norm_squared_lower = _vector_norm_squared_lower(covector_p)
    positive_energy_lower = (
        covector_p_norm_squared_lower
        + mass_squared_interval.lower * covector_q_norm_squared_lower
    )
    return {
        "detector": detector,
        "switch_id": switch_id,
        "two_j": two_j,
        "column": column,
        "partition_count": partition_count,
        "cell_width": str(width),
        "mass_squared_interval": mass_squared_interval.serialize(),
        "support_physical_time": [str(support_left), str(support_right)],
        "diagonal_value_endpoint_audit": diagonal_value,
        "diagonal_cosine_endpoint_audit": diagonal_cosine,
        "physical_two_form_value": [entry.serialize() for entry in physical_value],
        "physical_two_form_time_derivative": [
            entry.serialize() for entry in physical_time_derivative
        ],
        "coupling_stripped_advanced_covector_q": [
            entry.serialize() for entry in covector_q
        ],
        "coupling_stripped_advanced_covector_p": [
            entry.serialize() for entry in covector_p
        ],
        "positive_energy_lower_bound": {
            "covector_q_norm_squared_lower": str(covector_q_norm_squared_lower),
            "covector_p_norm_squared_lower": str(covector_p_norm_squared_lower),
            "energy_lower": str(positive_energy_lower),
            "formula": "E=<p,A p>+<q,L q> >= ||p||^2+m_squared_lower||q||^2",
            "strictly_positive": positive_energy_lower > 0,
        },
        "coupling_stripped_preparation_q": [
            entry.serialize() for entry in preparation_q
        ],
        "coupling_stripped_preparation_p": [
            entry.serialize() for entry in preparation_p
        ],
        "claim_boundary": "cell-partitioned positive-switch refinement of one finite detector-selected massive advanced preparation; no retained nonvanishing, detector record, response rank, infinite tail or recoil claim",
    }
