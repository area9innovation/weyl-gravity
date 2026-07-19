"""Finite detector-matched Berger absolute-g3 feedback contractions."""

from __future__ import annotations

from fractions import Fraction
from math import comb
from typing import Any, Mapping, Sequence

from closed_universe_observers.berger_recoil_detector_form_binding import (
    _interval_matrix,
    apply_spacetime_dhat1_to_detector_advanced_maxwell,
)
from closed_universe_observers.berger_recoil_free_emitter_retarded_channel import (
    evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right,
)
from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
    enclose_exact_mode_sine_kernel,
)
from closed_universe_observers.berger_recoil_massive_diagonal_preparation import (
    _block_diagonal_kernel_stage,
    _cosine_stage_from_sine_stage,
    _detector_center_physical_time,
    _switch_support,
    _translate_vector_polynomial,
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


def _matrix_vector(matrix: Matrix, vector: Vector) -> list[ComplexRationalInterval]:
    return [
        sum(
            (entry * value for entry, value in zip(row, vector)),
            ComplexRationalInterval.point(),
        )
        for row in matrix
    ]


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


def _polynomial_vector_upper(
    coefficients: Sequence[Vector], length: Fraction
) -> Fraction:
    return sum(
        (
            _vector_norm_upper(vector) * length**power
            for power, vector in enumerate(coefficients)
        ),
        Fraction(0),
    )


def _coefficient(
    coefficients: Sequence[Vector], power: int, dimension: int
) -> list[ComplexRationalInterval]:
    if power >= len(coefficients):
        return _zero_vector(dimension)
    return list(coefficients[power])


def _add_polynomials(
    left: Sequence[Vector], right: Sequence[Vector]
) -> list[list[ComplexRationalInterval]]:
    if not left or not right or len(left[0]) != len(right[0]):
        raise ValueError("polynomial vector dimensions must agree")
    dimension = len(left[0])
    return [
        [a + b for a, b in zip(
            _coefficient(left, power, dimension),
            _coefficient(right, power, dimension),
        )]
        for power in range(max(len(left), len(right)))
    ]


def _scale_polynomial_real_interval(
    coefficients: Sequence[Vector], scalar: RationalInterval
) -> list[list[ComplexRationalInterval]]:
    multiplier = ComplexRationalInterval(scalar, RationalInterval.point(0))
    return [[entry * multiplier for entry in vector] for vector in coefficients]


def _reverse_translate_polynomial(
    coefficients: Sequence[Vector], length: Fraction
) -> list[list[ComplexRationalInterval]]:
    """Return coefficients of ``P(length-s)`` in increasing powers of ``s``."""
    if not coefficients or not coefficients[0]:
        raise ValueError("polynomial must be nonempty")
    dimension = len(coefficients[0])
    output = [_zero_vector(dimension) for _ in coefficients]
    for input_power, vector in enumerate(coefficients):
        for output_power in range(input_power + 1):
            scale = (
                Fraction(comb(input_power, output_power))
                * length ** (input_power - output_power)
                * (-1) ** output_power
            )
            for row, entry in enumerate(vector):
                output[output_power][row] = (
                    output[output_power][row] + entry.scale(scale)
                )
    return output


def _spacetime_d_one_form_polynomial(
    *,
    field_coefficients: Sequence[Vector],
    field_remainder_upper: Fraction,
    time_derivative_coefficients: Sequence[Vector],
    time_derivative_remainder_upper: Fraction,
    two_j: int,
    radical_bits: int,
) -> tuple[list[list[ComplexRationalInterval]], Fraction]:
    """Apply ``d(phi,a)=(partial_t a-dSigma phi,dSigma a)``."""
    n = two_j + 1
    one_form_dimension = 4 * n
    if (
        not field_coefficients
        or not time_derivative_coefficients
        or any(len(row) != one_form_dimension for row in field_coefficients)
        or any(len(row) != one_form_dimension for row in time_derivative_coefficients)
    ):
        raise ValueError("Maxwell polynomial has the wrong one-form dimension")
    d0 = _interval_matrix(d_matrix(two_j, 0), radical_bits)
    d1 = _interval_matrix(d_matrix(two_j, 1), radical_bits)
    output = []
    for power in range(max(len(field_coefficients), len(time_derivative_coefficients))):
        field = _coefficient(field_coefficients, power, one_form_dimension)
        derivative = _coefficient(
            time_derivative_coefficients, power, one_form_dimension
        )
        phi, spatial = field[:n], field[n:]
        spatial_t = derivative[n:]
        temporal_two_form = [
            value + (-correction)
            for value, correction in zip(spatial_t, _matrix_vector(d0, phi))
        ]
        spatial_two_form = _matrix_vector(d1, spatial)
        output.append(temporal_two_form + spatial_two_form)
    remainder = Fraction(time_derivative_remainder_upper) + (
        _matrix_norm_upper(d0) + _matrix_norm_upper(d1)
    ) * Fraction(field_remainder_upper)
    return output, remainder


def _physical_advanced_emitter_polynomial(
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
    radical_bits: int,
) -> dict[str, object]:
    """Enclose the physical advanced emitter field across its switch slab."""
    switch_id = {"D0": "h_0", "D1": "h_1"}.get(detector)
    if switch_id is None:
        raise ValueError("detector must be D0 or D1")
    support_left, support_right = _switch_support(switch_certificate, switch_id)
    length = support_right - support_left
    center = _detector_center_physical_time(
        detector_profile_certificate, detector
    )
    source = apply_spacetime_dhat1_to_detector_advanced_maxwell(
        detector_image_certificate,
        detector=detector,
        two_j=two_j,
        column=column,
        radical_bits=radical_bits,
    )
    source_in_y = _translate_vector_polynomial(
        _deserialize_polynomial(source["polynomial_coefficients"]),
        center - support_right,
    )
    source_remainder = Fraction(
        source["remainder_audit"]["uniform_output_vector_remainder_upper"]
    )
    switch = emitter_switch_interval(
        switch_certificate,
        moment_certificate,
        switch_id=switch_id,
        physical_time_interval=RationalInterval(support_left, support_right),
    )
    switch_value = RationalInterval.from_serialized(switch["value"])
    switch_derivative = RationalInterval.from_serialized(
        switch["physical_time_derivative"]
    )
    switched_source = multiply_vector_polynomial_by_real_interval(
        coefficients=source_in_y,
        uniform_remainder_upper=source_remainder,
        multiplier=switch_value,
    )
    switched_source_coefficients = _deserialize_polynomial(
        switched_source["polynomial_coefficients"]
    )

    enclosures = {
        degree: enclose_exact_mode_sine_kernel(
            exact_kernel_certificate,
            two_j=two_j,
            family="massive_two_form",
            form_degree=degree,
            mass_squared_interval=mass_squared_interval,
            slab_length=length,
            radical_bits=radical_bits,
        )
        for degree in (1, 2)
    }
    sine = {
        degree: kernel_stage_from_sine_enclosure(enclosures[degree])
        for degree in (1, 2)
    }
    wave_two_stage = _block_diagonal_kernel_stage(sine[1], sine[2])
    wave_two = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=switched_source_coefficients,
        source_remainder_upper=Fraction(
            switched_source["uniform_remainder_upper"]
        ),
        kernel_stages=[wave_two_stage],
        slab_length=length,
        orientation="advanced",
    )

    n = two_j + 1
    temporal_two_form_source = [row[: 3 * n] for row in source_in_y]
    delta_switched_source = [
        _zero_vector(n)
        + [
            entry
            * ComplexRationalInterval(
                switch_derivative, RationalInterval.point(0)
            )
            for entry in temporal
        ]
        for temporal in temporal_two_form_source
    ]
    derivative_multiplier_upper = max(
        abs(switch_derivative.lower), abs(switch_derivative.upper)
    )
    delta_source_remainder = derivative_multiplier_upper * source_remainder
    degree_zero_enclosure = enclose_exact_mode_sine_kernel(
        exact_kernel_certificate,
        two_j=two_j,
        family="massive_two_form",
        form_degree=0,
        mass_squared_interval=mass_squared_interval,
        slab_length=length,
        radical_bits=radical_bits,
    )
    degree_zero_sine = kernel_stage_from_sine_enclosure(degree_zero_enclosure)
    wave_one_sine_stage = _block_diagonal_kernel_stage(
        # The one-form temporal/spatial blocks have degrees zero and one.
        degree_zero_sine,
        sine[1],
        label="massive_one_form_advanced_sine_block_diagonal",
    )
    wave_one_cosine_stage = _block_diagonal_kernel_stage(
        _cosine_stage_from_sine_stage(degree_zero_sine, degree_zero_enclosure),
        _cosine_stage_from_sine_stage(sine[1], enclosures[1]),
        label="massive_one_form_advanced_cosine_block_diagonal",
    )
    wave_one = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=delta_switched_source,
        source_remainder_upper=delta_source_remainder,
        kernel_stages=[wave_one_sine_stage],
        slab_length=length,
        orientation="advanced",
    )
    wave_one_dx = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=delta_switched_source,
        source_remainder_upper=delta_source_remainder,
        kernel_stages=[wave_one_cosine_stage],
        slab_length=length,
        orientation="advanced",
    )
    wave_one_coefficients = _deserialize_polynomial(
        wave_one["polynomial_coefficients"]
    )
    # x=t_right-t, hence physical partial_t=-partial_x.
    wave_one_time_derivative = [
        [-entry for entry in row]
        for row in _deserialize_polynomial(wave_one_dx["polynomial_coefficients"])
    ]
    d_wave_one, d_wave_one_remainder = _spacetime_d_one_form_polynomial(
        field_coefficients=wave_one_coefficients,
        field_remainder_upper=Fraction(wave_one["uniform_remainder_upper"]),
        time_derivative_coefficients=wave_one_time_derivative,
        time_derivative_remainder_upper=Fraction(
            wave_one_dx["uniform_remainder_upper"]
        ),
        two_j=two_j,
        radical_bits=radical_bits,
    )
    inverse_mass = RationalInterval(
        Fraction(1) / mass_squared_interval.upper,
        Fraction(1) / mass_squared_interval.lower,
    )
    physical = _add_polynomials(
        _deserialize_polynomial(wave_two["polynomial_coefficients"]),
        _scale_polynomial_real_interval(d_wave_one, inverse_mass),
    )
    inverse_mass_upper = max(abs(inverse_mass.lower), abs(inverse_mass.upper))
    physical_remainder = Fraction(wave_two["uniform_remainder_upper"]) + (
        inverse_mass_upper * d_wave_one_remainder
    )
    return {
        "switch_id": switch_id,
        "support_physical_time": [str(support_left), str(support_right)],
        "advanced_coordinate": "x=t_support_right-t",
        "physical_polynomial_coefficients_in_x": [
            [entry.serialize() for entry in row] for row in physical
        ],
        "physical_uniform_remainder_upper": str(physical_remainder),
        "switch_value_hull": switch["value"],
        "switch_physical_time_derivative_hull": switch[
            "physical_time_derivative"
        ],
        "physical_green_identity": "G_E,adv S=G_(P2+m2),adv S+m^-2 d G_(P1+m2),adv delta S",
        "switch_coderivative_identity": "delta(h dA_adv)=(0,h_prime alpha) because delta dA_adv=0 on the switch slab",
    }


def _conjugate(value: ComplexRationalInterval) -> ComplexRationalInterval:
    return ComplexRationalInterval(value.real, -value.imaginary)


def _integrate_lorentzian_two_form_pairing(
    *,
    advanced_coefficients: Sequence[Vector],
    advanced_remainder_upper: Fraction,
    retarded_source_coefficients: Sequence[Vector],
    retarded_source_remainder_upper: Fraction,
    length: Fraction,
    temporal_dimension: int,
) -> dict[str, object]:
    dimension = len(advanced_coefficients[0])
    if (
        not retarded_source_coefficients
        or len(retarded_source_coefficients[0]) != dimension
        or not 0 < temporal_dimension < dimension
    ):
        raise ValueError("two-form pairing dimensions do not agree")
    value = ComplexRationalInterval.point()
    for advanced_power, advanced in enumerate(advanced_coefficients):
        for source_power, source in enumerate(retarded_source_coefficients):
            coefficient = ComplexRationalInterval.point()
            for row, (left, right) in enumerate(zip(advanced, source)):
                term = _conjugate(left) * right
                coefficient = coefficient + (
                    -term if row < temporal_dimension else term
                )
            integral = length ** (advanced_power + source_power + 1) / Fraction(
                advanced_power + source_power + 1
            )
            value = value + coefficient.scale(integral)
    advanced_upper = _polynomial_vector_upper(advanced_coefficients, length)
    source_upper = _polynomial_vector_upper(
        retarded_source_coefficients, length
    )
    advanced_remainder_upper = Fraction(advanced_remainder_upper)
    retarded_source_remainder_upper = Fraction(retarded_source_remainder_upper)
    error = dimension * length * (
        advanced_upper * retarded_source_remainder_upper
        + source_upper * advanced_remainder_upper
        + advanced_remainder_upper * retarded_source_remainder_upper
    )
    box = RationalInterval(-error, error)
    enclosed = ComplexRationalInterval(value.real + box, value.imaginary + box)
    return {
        "coefficient_block_interval": enclosed.serialize(),
        "polynomial_pairing_without_box_remainder": value.serialize(),
        "uniform_pairing_remainder_upper": str(error),
        "lorentzian_two_form_pairing": "-<alpha,alpha_prime>_Sigma+<beta,beta_prime>_Sigma",
    }


def evaluate_detector_matched_absolute_g3_feedback_channel(
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
    """Evaluate ``I_aaa[two_j,column]`` with ``a`` matched to its emitter."""
    if mass_squared_interval.lower <= 0:
        raise ValueError("feedback mass squared must be strictly positive")
    if detector not in ("D0", "D1"):
        raise ValueError("detector must be D0 or D1")
    advanced = _physical_advanced_emitter_polynomial(
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
    leading = evaluate_free_emitter_first_retarded_maxwell_channel_at_support_right(
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
    if leading["support_physical_time"] != advanced["support_physical_time"]:
        raise ValueError("advanced and retarded matched-channel slabs disagree")
    support_left, support_right = map(Fraction, leading["support_physical_time"])
    length = support_right - support_left
    retarded = leading["first_retarded_maxwell_channel"]
    d_retarded, d_retarded_remainder = _spacetime_d_one_form_polynomial(
        field_coefficients=_deserialize_polynomial(
            retarded["field_polynomial_coefficients"]
        ),
        field_remainder_upper=Fraction(retarded["field_uniform_remainder_upper"]),
        time_derivative_coefficients=_deserialize_polynomial(
            retarded["time_derivative_polynomial_coefficients"]
        ),
        time_derivative_remainder_upper=Fraction(
            retarded["time_derivative_uniform_remainder_upper"]
        ),
        two_j=two_j,
        radical_bits=radical_bits,
    )
    switch_value = RationalInterval.from_serialized(
        advanced["switch_value_hull"]
    )
    switched_retarded = multiply_vector_polynomial_by_real_interval(
        coefficients=d_retarded,
        uniform_remainder_upper=d_retarded_remainder,
        multiplier=switch_value,
    )
    advanced_in_s = _reverse_translate_polynomial(
        _deserialize_polynomial(
            advanced["physical_polynomial_coefficients_in_x"]
        ),
        length,
    )
    pairing = _integrate_lorentzian_two_form_pairing(
        advanced_coefficients=advanced_in_s,
        advanced_remainder_upper=Fraction(
            advanced["physical_uniform_remainder_upper"]
        ),
        retarded_source_coefficients=_deserialize_polynomial(
            switched_retarded["polynomial_coefficients"]
        ),
        retarded_source_remainder_upper=Fraction(
            switched_retarded["uniform_remainder_upper"]
        ),
        length=length,
        temporal_dimension=3 * (two_j + 1),
    )
    label = "0" if detector == "D0" else "1"
    return {
        "channel_id": f"I_{label}{label}{label}",
        "detector": detector,
        "source_preparation": detector,
        "feedback_emitter": detector,
        "two_j": two_j,
        "column": column,
        "mass_squared_interval": mass_squared_interval.serialize(),
        "support_physical_time": leading["support_physical_time"],
        "green_adjoint_reduction": (
            f"I_{label}{label}{label}=<V_{label}^adv,"
            f"h_{label} d A_{label}^lead,ret>"
        ),
        "advanced_physical_emitter": advanced,
        "leading_retarded_channel_boundary": leading["claim_boundary"],
        "retarded_switched_field_strength": {
            "polynomial_coefficients_in_s": switched_retarded[
                "polynomial_coefficients"
            ],
            "uniform_remainder_upper": switched_retarded[
                "uniform_remainder_upper"
            ],
        },
        "pairing": pairing,
        "absolute_g3_monomial": f"g_{label}^3",
        "peter_weyl_weight_applied": False,
        "claim_boundary": (
            "one detector-matched coupling-stripped finite coefficient block "
            "I_aaa[two_j,k] before the Peter--Weyl reconstruction weight; no "
            "cross channel, shell sum, tail stop, numerical mass/coupling "
            "specialization, nonzero/sign claim, tangent-cone or quantum claim"
        ),
    }
