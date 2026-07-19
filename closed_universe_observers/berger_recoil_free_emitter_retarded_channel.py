"""Finite canonical emitter evolution and first retarded Maxwell channel."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping, Sequence

from closed_universe_observers.berger_recoil_detector_form_binding import (
    _interval_matrix,
)
from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
    enclose_exact_mode_sine_kernel,
)
from closed_universe_observers.berger_recoil_massive_diagonal_preparation import (
    _adjoint,
    _block_diagonal_kernel_stage,
    _cosine_stage_from_sine_stage,
    _evaluate_polynomial_with_remainder,
    evaluate_coupling_stripped_positive_energy_preparation_at_support_left,
)
from closed_universe_observers.berger_recoil_matrix_interval import (
    evaluate_matrix_green_time_convolution_interval,
    kernel_stage_from_sine_enclosure,
    multiply_vector_polynomial_by_real_interval,
)
from closed_universe_observers.berger_recoil_switch_intervals import (
    emitter_switch_interval,
)
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import (
    d_matrix,
)


Vector = Sequence[ComplexRationalInterval]
Matrix = Sequence[Sequence[ComplexRationalInterval]]


def _complex_from_serialized(
    value: Mapping[str, Mapping[str, str]],
) -> ComplexRationalInterval:
    return ComplexRationalInterval(
        RationalInterval.from_serialized(value["real"]),
        RationalInterval.from_serialized(value["imaginary"]),
    )


def _deserialize_polynomial(
    rows: Sequence[Sequence[Mapping[str, Any]]],
) -> list[list[ComplexRationalInterval]]:
    return [[_complex_from_serialized(entry) for entry in row] for row in rows]


def _zero_vector(dimension: int) -> list[ComplexRationalInterval]:
    return [ComplexRationalInterval.point() for _ in range(dimension)]


def _identity_matrix(dimension: int) -> list[list[ComplexRationalInterval]]:
    return [
        [ComplexRationalInterval.point(int(row == column)) for column in range(dimension)]
        for row in range(dimension)
    ]


def _matrix_vector(matrix: Matrix, vector: Vector) -> list[ComplexRationalInterval]:
    return [
        sum(
            (entry * value for entry, value in zip(row, vector)),
            ComplexRationalInterval.point(),
        )
        for row in matrix
    ]


def _matrix_multiply(left: Matrix, right: Matrix) -> list[list[ComplexRationalInterval]]:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("matrix dimensions do not compose")
    columns = len(right[0])
    if any(len(row) != len(left[0]) for row in left) or any(
        len(row) != columns for row in right
    ):
        raise ValueError("ragged matrix")
    return [
        [
            sum(
                (left[row][inner] * right[inner][column] for inner in range(len(right))),
                ComplexRationalInterval.point(),
            )
            for column in range(columns)
        ]
        for row in range(len(left))
    ]


def _matrix_add(left: Matrix, right: Matrix) -> list[list[ComplexRationalInterval]]:
    if len(left) != len(right) or any(len(a) != len(b) for a, b in zip(left, right)):
        raise ValueError("matrix dimensions must agree")
    return [[a + b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def _matrix_norm_upper(matrix: Matrix) -> Fraction:
    return max(
        (
            sum((entry.absolute_upper() for entry in row), Fraction(0))
            for row in matrix
        ),
        default=Fraction(0),
    )


def _vector_norm_upper(vector: Vector) -> Fraction:
    return max((entry.absolute_upper() for entry in vector), default=Fraction(0))


def _kernel_action(
    stage: Mapping[str, Any], vector: Vector
) -> tuple[list[list[ComplexRationalInterval]], Fraction]:
    matrices = stage["coefficient_matrices"]
    if any(len(matrix) != len(vector) for matrix in matrices):
        raise ValueError("kernel and vector dimensions do not agree")
    return (
        [_matrix_vector(matrix, vector) for matrix in matrices],
        Fraction(stage["uniform_remainder_upper"]) * _vector_norm_upper(vector),
    )


def _add_polynomial_enclosures(
    *terms: tuple[Sequence[Vector], Fraction]
) -> tuple[list[list[ComplexRationalInterval]], Fraction]:
    if not terms or not terms[0][0]:
        raise ValueError("at least one nonempty polynomial is required")
    dimension = len(terms[0][0][0])
    length = max(len(coefficients) for coefficients, _ in terms)
    output = [_zero_vector(dimension) for _ in range(length)]
    remainder = Fraction(0)
    for coefficients, term_remainder in terms:
        if any(len(vector) != dimension for vector in coefficients):
            raise ValueError("polynomial vector dimensions must agree")
        for power, vector in enumerate(coefficients):
            output[power] = [a + b for a, b in zip(output[power], vector)]
        remainder += Fraction(term_remainder)
    return output, remainder


def _negate_polynomial(
    coefficients: Sequence[Vector], remainder: Fraction
) -> tuple[list[list[ComplexRationalInterval]], Fraction]:
    return [[-entry for entry in vector] for vector in coefficients], Fraction(remainder)


def _static_matrix_action(
    matrix: Matrix,
    coefficients: Sequence[Vector],
    remainder: Fraction,
) -> tuple[list[list[ComplexRationalInterval]], Fraction]:
    return (
        [_matrix_vector(matrix, vector) for vector in coefficients],
        _matrix_norm_upper(matrix) * Fraction(remainder),
    )


def _scale_matrix_diagonal(
    matrix: Matrix, diagonal: RationalInterval
) -> list[list[ComplexRationalInterval]]:
    scalar = ComplexRationalInterval(diagonal, RationalInterval.point(0))
    return [
        [entry + (scalar if row == column else ComplexRationalInterval.point()) for column, entry in enumerate(entries)]
        for row, entries in enumerate(matrix)
    ]


def evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right(
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
    radical_bits: int = 80,
) -> dict[str, object]:
    """Evolve ``tilde_u``, form ``delta(h K)``, and apply ``G_A,ret`` once.

    The result is coupling-stripped and stops at the support-right Maxwell
    Cauchy pair.  It is not a detector contraction or a recoil coefficient.
    """
    if mass_squared_interval.lower <= 0:
        raise ValueError("free emitter evolution requires positive mass squared")
    preparation = evaluate_coupling_stripped_positive_energy_preparation_at_support_left(
        detector_image_certificate=detector_image_certificate,
        detector_profile_certificate=detector_profile_certificate,
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        exact_kernel_certificate=exact_kernel_certificate,
        detector=detector,
        two_j=two_j,
        column=column,
        mass_squared_interval=mass_squared_interval,
        radical_bits=radical_bits,
    )
    switch_id = {"D0": "h_0", "D1": "h_1"}.get(detector)
    if switch_id is None:
        raise ValueError("detector must be D0 or D1")
    switch_row = next(
        row
        for row in switch_certificate["causal_support_audit"]["switches"]
        if row["id"] == switch_id
    )
    support_left, support_right = map(Fraction, switch_row["support_physical_time"])
    if Fraction(preparation["support_left_physical_time"]) != support_left:
        raise ValueError("preparation and emitter switch support-left slices disagree")
    slab_length = support_right - support_left

    q0 = [
        _complex_from_serialized(entry)
        for entry in preparation["coupling_stripped_preparation_q"]
    ]
    p0 = [
        _complex_from_serialized(entry)
        for entry in preparation["coupling_stripped_preparation_p"]
    ]
    dimension = 3 * (two_j + 1)
    if len(q0) != dimension or len(p0) != dimension:
        raise ValueError("canonical preparation has the wrong spatial two-form dimension")

    d1 = _interval_matrix(d_matrix(two_j, 1), radical_bits)
    delta_two = _adjoint(d1)
    d2 = _interval_matrix(d_matrix(two_j, 2), radical_bits)
    delta_three = _adjoint(d2)
    inverse_mass = RationalInterval(
        Fraction(1) / mass_squared_interval.upper,
        Fraction(1) / mass_squared_interval.lower,
    )
    identity = _identity_matrix(dimension)
    a_operator = _matrix_add(
        identity,
        [
            [entry * ComplexRationalInterval(inverse_mass, RationalInterval.point(0)) for entry in row]
            for row in _matrix_multiply(d1, delta_two)
        ],
    )
    ell_operator = _scale_matrix_diagonal(
        _matrix_multiply(delta_three, d2), mass_squared_interval
    )
    a_p0 = _matrix_vector(a_operator, p0)
    ell_q0 = _matrix_vector(ell_operator, q0)

    massive_enclosure = enclose_exact_mode_sine_kernel(
        exact_kernel_certificate,
        two_j=two_j,
        family="massive_two_form",
        form_degree=2,
        mass_squared_interval=mass_squared_interval,
        slab_length=slab_length,
        radical_bits=radical_bits,
    )
    sine_stage = kernel_stage_from_sine_enclosure(
        massive_enclosure,
        label=f"massive_two_form_degree2_{detector}_two_j{two_j}",
    )
    cosine_stage = _cosine_stage_from_sine_stage(sine_stage, massive_enclosure)
    q_cos = _kernel_action(cosine_stage, q0)
    q_sine = _kernel_action(sine_stage, a_p0)
    q_coefficients, q_remainder = _add_polynomial_enclosures(q_cos, q_sine)
    p_cos = _kernel_action(cosine_stage, p0)
    p_sine = _negate_polynomial(*_kernel_action(sine_stage, ell_q0))
    p_coefficients, p_remainder = _add_polynomial_enclosures(p_cos, p_sine)
    initial_q_exact = q_coefficients[0] == q0
    initial_p_exact = p_coefficients[0] == p0
    if not initial_q_exact or not initial_p_exact:
        raise AssertionError("free emitter evolution lost its support-left Cauchy data")

    alpha_coefficients, alpha_remainder = _static_matrix_action(
        delta_two, p_coefficients, p_remainder
    )
    inverse_mass_scalar = ComplexRationalInterval(
        inverse_mass, RationalInterval.point(0)
    )
    alpha_coefficients = [
        [entry * inverse_mass_scalar for entry in vector]
        for vector in alpha_coefficients
    ]
    alpha_remainder *= max(abs(inverse_mass.lower), abs(inverse_mass.upper))

    switch = emitter_switch_interval(
        switch_certificate,
        moment_certificate,
        switch_id=switch_id,
        physical_time_interval=RationalInterval(support_left, support_right),
    )
    derivative_hull = RationalInterval.from_serialized(
        switch["physical_time_derivative"]
    )
    spatial_source = multiply_vector_polynomial_by_real_interval(
        coefficients=alpha_coefficients,
        uniform_remainder_upper=alpha_remainder,
        multiplier=derivative_hull,
    )
    spatial_source_coefficients = _deserialize_polynomial(
        spatial_source["polynomial_coefficients"]
    )
    temporal_dimension = two_j + 1
    spacetime_source_coefficients = [
        _zero_vector(temporal_dimension) + vector
        for vector in spatial_source_coefficients
    ]

    maxwell_enclosures = {
        degree: enclose_exact_mode_sine_kernel(
            exact_kernel_certificate,
            two_j=two_j,
            family="Maxwell",
            form_degree=degree,
            mass_squared_interval=RationalInterval.point(0),
            slab_length=slab_length,
            radical_bits=radical_bits,
        )
        for degree in (0, 1)
    }
    maxwell_sine_components = {
        degree: kernel_stage_from_sine_enclosure(maxwell_enclosures[degree])
        for degree in (0, 1)
    }
    maxwell_cosine_components = {
        degree: _cosine_stage_from_sine_stage(
            maxwell_sine_components[degree], maxwell_enclosures[degree]
        )
        for degree in (0, 1)
    }
    maxwell_sine = _block_diagonal_kernel_stage(
        maxwell_sine_components[0],
        maxwell_sine_components[1],
        label="Maxwell_spacetime_retarded_sine_block_diagonal",
    )
    maxwell_cosine = _block_diagonal_kernel_stage(
        maxwell_cosine_components[0],
        maxwell_cosine_components[1],
        label="Maxwell_spacetime_retarded_cosine_block_diagonal",
    )
    source_remainder = Fraction(spatial_source["uniform_remainder_upper"])
    retarded_value = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=spacetime_source_coefficients,
        source_remainder_upper=source_remainder,
        kernel_stages=[maxwell_sine],
        slab_length=slab_length,
        orientation="retarded",
    )
    retarded_derivative = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=spacetime_source_coefficients,
        source_remainder_upper=source_remainder,
        kernel_stages=[maxwell_cosine],
        slab_length=slab_length,
        orientation="retarded",
    )
    value_coefficients = _deserialize_polynomial(
        retarded_value["polynomial_coefficients"]
    )
    derivative_coefficients = _deserialize_polynomial(
        retarded_derivative["polynomial_coefficients"]
    )
    zero = ComplexRationalInterval.point()
    source_temporal_block_zero = all(
        entry == zero
        for vector in spacetime_source_coefficients
        for entry in vector[:temporal_dimension]
    )
    retarded_field_initial_zero = all(
        entry == zero for entry in value_coefficients[0]
    )
    retarded_derivative_initial_zero = all(
        entry == zero for entry in derivative_coefficients[0]
    )
    if not (
        source_temporal_block_zero
        and retarded_field_initial_zero
        and retarded_derivative_initial_zero
    ):
        raise AssertionError("causal source/retarded initial-data audit failed")
    support_right_value = _evaluate_polynomial_with_remainder(
        value_coefficients,
        slab_length,
        Fraction(retarded_value["uniform_remainder_upper"]),
    )
    support_right_derivative = _evaluate_polynomial_with_remainder(
        derivative_coefficients,
        slab_length,
        Fraction(retarded_derivative["uniform_remainder_upper"]),
    )
    return {
        "detector": detector,
        "switch_id": switch_id,
        "two_j": two_j,
        "column": column,
        "mass_squared_interval": mass_squared_interval.serialize(),
        "support_physical_time": [str(support_left), str(support_right)],
        "causal_coordinate": "s=t-support_left",
        "causal_initial_data_audit": {
            "free_evolution_q_at_support_left_equals_q0": initial_q_exact,
            "free_evolution_p_at_support_left_equals_p0": initial_p_exact,
            "switched_current_temporal_block_structural_zero": source_temporal_block_zero,
            "retarded_maxwell_field_at_support_left_structural_zero": retarded_field_initial_zero,
            "retarded_maxwell_time_derivative_at_support_left_structural_zero": retarded_derivative_initial_zero,
        },
        "canonical_free_evolution": {
            "q_polynomial_coefficients": [
                [entry.serialize() for entry in vector]
                for vector in q_coefficients
            ],
            "q_uniform_remainder_upper": str(q_remainder),
            "p_polynomial_coefficients": [
                [entry.serialize() for entry in vector]
                for vector in p_coefficients
            ],
            "p_uniform_remainder_upper": str(p_remainder),
            "alpha_polynomial_coefficients": [
                [entry.serialize() for entry in vector]
                for vector in alpha_coefficients
            ],
            "alpha_uniform_remainder_upper": str(alpha_remainder),
            "formula": "q=C_H q0+S_H A p0; p=C_H p0-S_H L q0; alpha=m^-2 deltaSigma p",
        },
        "switched_current": {
            "spacetime_one_form_order": ["temporal_scalar", "spatial_one_form"],
            "formula": "J=delta(hK)=(0,h_prime alpha) on delta K=0",
            "switch_physical_time_derivative_hull": switch[
                "physical_time_derivative"
            ],
            "polynomial_coefficients": [
                [entry.serialize() for entry in vector]
                for vector in spacetime_source_coefficients
            ],
            "uniform_remainder_upper": spatial_source[
                "uniform_remainder_upper"
            ],
            "temporal_block_structural_zero": True,
            "conservation_identity": "delta J=delta^2(hK)=0; equivalently deltaSigma alpha=0",
        },
        "first_retarded_maxwell_channel": {
            "field_polynomial_coefficients": retarded_value[
                "polynomial_coefficients"
            ],
            "field_uniform_remainder_upper": retarded_value[
                "uniform_remainder_upper"
            ],
            "time_derivative_polynomial_coefficients": retarded_derivative[
                "polynomial_coefficients"
            ],
            "time_derivative_uniform_remainder_upper": retarded_derivative[
                "uniform_remainder_upper"
            ],
            "support_right_field": [
                entry.serialize() for entry in support_right_value
            ],
            "support_right_time_derivative": [
                entry.serialize() for entry in support_right_derivative
            ],
        },
        "claim_boundary": "finite coupling-stripped U_E evolution, conserved switched current, and first G_A,ret Maxwell Cauchy pair at the emitter support-right slice through two_j=4; retained nonvanishing, propagation to a detector window, Q_a contraction, response rank, feedback recoil, infinite tail and tangent-cone restriction remain open",
    }
