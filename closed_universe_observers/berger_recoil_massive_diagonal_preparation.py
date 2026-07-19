"""Finite switched detector source and diagonal massive advanced-wave image."""

from __future__ import annotations

from functools import lru_cache
from fractions import Fraction
from math import comb
from math import factorial
from typing import Any, Mapping, Sequence

import sympy as sp

from closed_universe_observers.berger_recoil_detector_form_binding import (
    _interval_matrix,
    apply_spacetime_dhat1_to_detector_advanced_maxwell,
)
from closed_universe_observers.berger_recoil_interval_stream import (
    ComplexRationalInterval,
    RationalInterval,
    enclose_exact_mode_sine_kernel,
)
from closed_universe_observers.berger_recoil_matrix_interval import (
    evaluate_matrix_green_time_convolution_interval,
    kernel_stage_from_sine_enclosure,
    multiply_vector_polynomial_by_real_interval,
)
from closed_universe_observers.berger_recoil_switch_intervals import emitter_switch_interval
from closed_universe_observers.generate_berger_peter_weyl_form_laplacian import d_matrix


Vector = Sequence[ComplexRationalInterval]
Matrix = Sequence[Sequence[ComplexRationalInterval]]


def _complex_from_serialized(value: Mapping[str, Mapping[str, str]]) -> ComplexRationalInterval:
    return ComplexRationalInterval(
        RationalInterval.from_serialized(value["real"]),
        RationalInterval.from_serialized(value["imaginary"]),
    )


def _deserialize_polynomial(rows: Sequence[Sequence[Mapping[str, Any]]]) -> list[list[ComplexRationalInterval]]:
    return [[_complex_from_serialized(entry) for entry in vector] for vector in rows]


def _translate_vector_polynomial(
    coefficients: Sequence[Vector], shift: Fraction
) -> list[list[ComplexRationalInterval]]:
    """Return coefficients of ``P(shift+y)`` from coefficients of ``P(T)``."""
    if not coefficients or not coefficients[0]:
        raise ValueError("vector polynomial must be nonempty")
    dimension = len(coefficients[0])
    if any(len(vector) != dimension for vector in coefficients):
        raise ValueError("vector polynomial dimensions must agree")
    shift = Fraction(shift)
    output = [
        [ComplexRationalInterval.point() for _ in range(dimension)]
        for _ in coefficients
    ]
    for input_power, vector in enumerate(coefficients):
        for output_power in range(input_power + 1):
            scale = Fraction(comb(input_power, output_power)) * shift ** (
                input_power - output_power
            )
            for row, entry in enumerate(vector):
                output[output_power][row] = output[output_power][row] + entry.scale(scale)
    return output


def translate_vector_polynomial(
    *, coefficients: Sequence[Vector], shift: Fraction
) -> dict[str, object]:
    translated = _translate_vector_polynomial(coefficients, shift)
    return {
        "shift": str(Fraction(shift)),
        "polynomial_coefficients": [
            [entry.serialize() for entry in vector] for vector in translated
        ],
        "claim_boundary": "exact affine translation P(T)->P(shift+y) of a supplied complex interval vector polynomial",
    }


def _detector_center_physical_time(
    profile_certificate: Mapping[str, Any], detector: str
) -> Fraction:
    if profile_certificate.get("result_id") != "BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS":
        raise ValueError("wrong detector profile certificate")
    profiles = profile_certificate["exact_detector_profiles"]
    row = next((value for value in profiles["detectors"] if value["id"] == detector), None)
    if row is None:
        raise ValueError("selected detector profile is absent")
    return Fraction(row["clock_center"]) / Fraction(profiles["clock_rate_dTheta_dt"])


def _switch_support(
    switch_certificate: Mapping[str, Any], switch_id: str
) -> tuple[Fraction, Fraction]:
    if switch_certificate.get("result_id") != "BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES":
        raise ValueError("wrong exact switch certificate")
    row = next(
        (
            value
            for value in switch_certificate["causal_support_audit"]["switches"]
            if value["id"] == switch_id
        ),
        None,
    )
    if row is None:
        raise ValueError("selected emitter switch is absent")
    return tuple(Fraction(value) for value in row["support_physical_time"])


def _evaluate_polynomial_with_remainder(
    coefficients: Sequence[Vector], argument: Fraction, remainder: Fraction
) -> list[ComplexRationalInterval]:
    if remainder < 0:
        raise ValueError("uniform remainder must be nonnegative")
    dimension = len(coefficients[0])
    value = [ComplexRationalInterval.point() for _ in range(dimension)]
    for power, vector in enumerate(coefficients):
        for row, entry in enumerate(vector):
            value[row] = value[row] + entry.scale(argument**power)
    error = RationalInterval(-remainder, remainder)
    return [ComplexRationalInterval(entry.real + error, entry.imaginary + error) for entry in value]


def _block_diagonal_kernel_stage(
    temporal_stage: Mapping[str, Any],
    spatial_stage: Mapping[str, Any],
    *,
    label: str = "massive_two_form_spacetime_block_diagonal",
) -> dict[str, object]:
    temporal = temporal_stage["coefficient_matrices"]
    spatial = spatial_stage["coefficient_matrices"]
    if len(temporal) != len(spatial):
        raise ValueError("temporal and spatial kernel polynomial lengths must agree")
    temporal_dimension = len(temporal[0])
    spatial_dimension = len(spatial[0])
    zero = ComplexRationalInterval.point()
    matrices = []
    for temporal_matrix, spatial_matrix in zip(temporal, spatial):
        matrix = [
            [zero for _ in range(temporal_dimension + spatial_dimension)]
            for _ in range(temporal_dimension + spatial_dimension)
        ]
        for row in range(temporal_dimension):
            for column in range(temporal_dimension):
                matrix[row][column] = temporal_matrix[row][column]
        for row in range(spatial_dimension):
            for column in range(spatial_dimension):
                matrix[temporal_dimension + row][temporal_dimension + column] = spatial_matrix[row][column]
        matrices.append(matrix)
    return {
        "label": label,
        "coefficient_matrices": matrices,
        "uniform_remainder_upper": max(
            Fraction(temporal_stage["uniform_remainder_upper"]),
            Fraction(spatial_stage["uniform_remainder_upper"]),
        ),
        "nonzero_tau_powers": sorted(
            set(temporal_stage["nonzero_tau_powers"])
            | set(spatial_stage["nonzero_tau_powers"])
        ),
        "block_dimensions": [temporal_dimension, spatial_dimension],
    }


def _cosine_stage_from_sine_stage(
    sine_stage: Mapping[str, Any], enclosure: Mapping[str, Any]
) -> dict[str, object]:
    powers = sine_stage["nonzero_tau_powers"]
    dimension = len(sine_stage["coefficient_matrices"][0])
    maximum = max(powers) - 1
    zero = ComplexRationalInterval.point()
    matrices = [
        [[zero for _ in range(dimension)] for _ in range(dimension)]
        for _ in range(maximum + 1)
    ]
    for sine_power in powers:
        matrices[sine_power - 1] = [
            [entry.scale(sine_power) for entry in row]
            for row in sine_stage["coefficient_matrices"][sine_power]
        ]
    order = int(enclosure["series_order"])
    y = Fraction(enclosure["dimensionless_norm_upper"])
    ratio = y / Fraction((2 * order + 3) * (2 * order + 4))
    if ratio >= 1:
        raise ValueError("cosine tail majorant is not contractive")
    remainder = y ** (order + 1) / factorial(2 * order + 2) / (1 - ratio)
    return {
        "label": "cosine_derivative_stage",
        "coefficient_matrices": matrices,
        "uniform_remainder_upper": remainder,
        "nonzero_tau_powers": [power - 1 for power in powers],
    }


def _matrix_vector(matrix: Matrix, vector: Vector) -> list[ComplexRationalInterval]:
    return [
        sum((entry * value for entry, value in zip(row, vector)), ComplexRationalInterval.point())
        for row in matrix
    ]


def _adjoint(matrix: Matrix) -> list[list[ComplexRationalInterval]]:
    return [
        [
            ComplexRationalInterval(matrix[row][column].real, -matrix[row][column].imaginary)
            for row in range(len(matrix))
        ]
        for column in range(len(matrix[0]))
    ]


def _add(*vectors: Vector) -> list[ComplexRationalInterval]:
    return [
        sum((vector[row] for vector in vectors), ComplexRationalInterval.point())
        for row in range(len(vectors[0]))
    ]


def _scale_real_interval(vector: Vector, scalar: RationalInterval) -> list[ComplexRationalInterval]:
    multiplier = ComplexRationalInterval(scalar, RationalInterval.point(0))
    return [entry * multiplier for entry in vector]


@lru_cache(maxsize=None)
def coclosed_two_form_projector(two_j: int) -> sp.Matrix:
    """Return the exact orthogonal projector onto ``ker(delta_Sigma:Omega2->Omega1)``."""
    if two_j < 0:
        raise ValueError("two_j must be nonnegative")
    delta_two = d_matrix(two_j, 1).conjugate().T
    kernel = delta_two.nullspace()
    dimension = 3 * (two_j + 1)
    if not kernel:
        return sp.zeros(dimension)
    basis = sp.Matrix.hstack(*kernel)
    gram = basis.conjugate().T * basis
    return sp.simplify(basis * gram.inv() * basis.conjugate().T)


def coclosed_two_form_projector_audit(two_j: int) -> dict[str, object]:
    """Audit the exact Hodge projector used by the positive-energy trace."""
    projector = coclosed_two_form_projector(two_j)
    delta_two = d_matrix(two_j, 1).conjugate().T
    exact_two_forms = d_matrix(two_j, 1)

    def defects(matrix: sp.Matrix) -> int:
        return sum(sp.simplify(entry) != 0 for entry in matrix)

    return {
        "two_j": two_j,
        "spatial_two_form_dimension": projector.rows,
        "coclosed_rank": projector.rank(),
        "idempotence_defect_count": defects(projector * projector - projector),
        "self_adjoint_defect_count": defects(projector.conjugate().T - projector),
        "coderivative_defect_count": defects(delta_two * projector),
        "exact_form_annihilation_defect_count": defects(projector * exact_two_forms),
        "temporal_component_reconstruction_defect_count": defects(delta_two * projector),
        "clock_switched_observer_current_defect_count": defects(delta_two * projector),
        "clock_switched_observer_current_identity": "on q=Pi_co q and p=Pi_co p, alpha=m^-2 deltaSigma p=0 and free preservation gives delta(hK)=h_prime alpha=0",
    }


def evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left(
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
    """Enclose ``G_(Delta2+mu2),adv[h_a Dhat1 A_a^adv]`` at ``inf supp h_a``.

    This is the diagonal massive wave inverse, not the physical
    ``(I+mu^-2 Dhat_1 Deltahat_2)`` two-form Green operator.
    """
    if detector not in ("D0", "D1"):
        raise ValueError("detector must be D0 or D1")
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
    source_in_T = _deserialize_polynomial(dhat["polynomial_coefficients"])
    source_in_y = _translate_vector_polynomial(source_in_T, shift)
    source_remainder = Fraction(
        dhat["remainder_audit"]["uniform_output_vector_remainder_upper"]
    )
    switch = emitter_switch_interval(
        switch_certificate,
        moment_certificate,
        switch_id=switch_id,
        physical_time_interval=RationalInterval(support_left, support_right),
    )
    switch_value = RationalInterval.from_serialized(switch["value"])
    switched = multiply_vector_polynomial_by_real_interval(
        coefficients=source_in_y,
        uniform_remainder_upper=source_remainder,
        multiplier=switch_value,
    )
    switched_coefficients = _deserialize_polynomial(switched["polynomial_coefficients"])

    kernel_enclosures = {
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
    component_stages = {
        degree: kernel_stage_from_sine_enclosure(
            kernel_enclosures[degree],
            label=f"massive_two_form_degree{degree}_{detector}_two_j{two_j}",
        )
        for degree in (1, 2)
    }
    kernel_stage = _block_diagonal_kernel_stage(component_stages[1], component_stages[2])
    convolution = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=switched_coefficients,
        source_remainder_upper=Fraction(switched["uniform_remainder_upper"]),
        kernel_stages=[kernel_stage],
        slab_length=slab_length,
        orientation="advanced",
    )
    image_polynomial = _deserialize_polynomial(convolution["polynomial_coefficients"])
    image_remainder = Fraction(convolution["uniform_remainder_upper"])
    support_left_image = _evaluate_polynomial_with_remainder(
        image_polynomial, slab_length, image_remainder
    )
    return {
        "detector": detector,
        "switch_id": switch_id,
        "two_j": two_j,
        "column": column,
        "mass_squared_interval": mass_squared_interval.serialize(),
        "support_physical_time": [str(support_left), str(support_right)],
        "advanced_coordinate": "y=t_support_right-source_time; x=t_support_right-evaluation_time",
        "support_left_coordinate": str(slab_length),
        "detector_T_to_source_y_shift": str(shift),
        "switch_value_hull": switch["value"],
        "source_polynomial_coefficients_in_y": [
            [entry.serialize() for entry in vector] for vector in switched_coefficients
        ],
        "source_uniform_remainder_upper": switched["uniform_remainder_upper"],
        "kernel_nonzero_tau_powers": kernel_stage["nonzero_tau_powers"],
        "kernel_block_dimensions": kernel_stage["block_dimensions"],
        "component_kernel_uniform_remainder_uppers": {
            str(degree): str(component_stages[degree]["uniform_remainder_upper"])
            for degree in (1, 2)
        },
        "kernel_uniform_remainder_upper": str(kernel_stage["uniform_remainder_upper"]),
        "image_polynomial_coefficients_in_x": convolution["polynomial_coefficients"],
        "image_uniform_remainder_upper": convolution["uniform_remainder_upper"],
        "support_left_diagonal_massive_wave_image": [
            entry.serialize() for entry in support_left_image
        ],
        "claim_boundary": "finite switched detector-selected diagonal massive degree-two advanced-wave image at the support-left slice; physical Proca correction, Cauchy momentum/dual and I_abc remain open",
    }


def evaluate_physical_massive_advanced_cauchy_pair_at_support_left(
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
    """Apply ``I+mu^-2 Dhat_1 Deltahat_2`` and export ``(K,partial_t K)``."""
    if switch_certificate.get("flags", {}).get("SWITCHES_C_INFINITY_COMPACT_SUPPORTED") is not True:
        raise ValueError("switch boundary flatness is not certified")
    diagonal = evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left(
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
    support_left, support_right = map(Fraction, diagonal["support_physical_time"])
    length = support_right - support_left
    switch_endpoint = emitter_switch_interval(
        switch_certificate,
        moment_certificate,
        switch_id=diagonal["switch_id"],
        physical_time_interval=RationalInterval.point(support_left),
    )
    if not switch_endpoint["structural_zero"]:
        raise ValueError("support-left switch endpoint is not structural zero")
    source = _deserialize_polynomial(diagonal["source_polynomial_coefficients_in_y"])
    source_remainder = Fraction(diagonal["source_uniform_remainder_upper"])
    component_enclosures = {
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
    sine_components = {
        degree: kernel_stage_from_sine_enclosure(component_enclosures[degree])
        for degree in (1, 2)
    }
    cosine_components = {
        degree: _cosine_stage_from_sine_stage(
            sine_components[degree], component_enclosures[degree]
        )
        for degree in (1, 2)
    }
    cosine_stage = _block_diagonal_kernel_stage(cosine_components[1], cosine_components[2])
    derivative_convolution = evaluate_matrix_green_time_convolution_interval(
        source_coefficients=source,
        source_remainder_upper=source_remainder,
        kernel_stages=[cosine_stage],
        slab_length=length,
        orientation="advanced",
    )
    dx_polynomial = _deserialize_polynomial(derivative_convolution["polynomial_coefficients"])
    dx_value = _evaluate_polynomial_with_remainder(
        dx_polynomial, length, Fraction(derivative_convolution["uniform_remainder_upper"])
    )
    value = [_complex_from_serialized(entry) for entry in diagonal["support_left_diagonal_massive_wave_image"]]
    time_derivative = [-entry for entry in dx_value]

    # A is recovered exactly from the sine coefficient -A*tau^3/3! in each block.
    sine_stage = _block_diagonal_kernel_stage(sine_components[1], sine_components[2])
    operator = [
        [entry.scale(-6) for entry in row]
        for row in sine_stage["coefficient_matrices"][3]
    ]
    second_time_derivative = [-entry for entry in _matrix_vector(operator, value)]
    third_time_derivative = [-entry for entry in _matrix_vector(operator, time_derivative)]

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
        Fraction(1, 1) / mass_squared_interval.upper,
        Fraction(1, 1) / mass_squared_interval.lower,
    )
    physical_value = _add(value, _scale_real_interval(correction_top + correction_bottom, inverse_mass))
    physical_time_derivative = _add(
        time_derivative,
        _scale_real_interval(correction_t_top + correction_t_bottom, inverse_mass),
    )
    return {
        "detector": detector,
        "two_j": two_j,
        "column": column,
        "mass_squared_interval": mass_squared_interval.serialize(),
        "support_left_physical_time": str(support_left),
        "endpoint_flatness": "h_a and every physical-time derivative vanish at the compact support boundary",
        "cosine_nonzero_tau_powers": cosine_stage["nonzero_tau_powers"],
        "diagonal_wave_time_derivative": [entry.serialize() for entry in time_derivative],
        "physical_two_form_value": [entry.serialize() for entry in physical_value],
        "physical_two_form_time_derivative": [entry.serialize() for entry in physical_time_derivative],
        "cauchy_pair_order": ["K_at_support_left", "partial_t_K_at_support_left"],
        "claim_boundary": "finite physical massive two-form advanced Cauchy pair through two_j=4 for a runtime positive mass interval; positive-energy dual, spatial tail and I_abc remain open",
    }


def evaluate_coupling_stripped_positive_energy_preparation_at_support_left(
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
    """Trace the physical field to canonical ``(q,p)`` and apply ``(-A p,Lq)``.

    For ``K=dt wedge alpha+beta``, the canonical spatial momentum is
    ``p=partial_t beta-d_Sigma alpha`` and ``q=beta``.  Eliminating the
    temporal component gives ``alpha=m^-2 delta_Sigma p`` and the Hamiltonian
    operators ``A=I+m^-2 d_Sigma delta_Sigma`` and
    ``L=delta_Sigma d_Sigma+m^2``.  Thus the positive-energy dual is
    ``(q,p)->(-A p,Lq)``.  The co-closed restriction would set ``alpha=0``
    and makes the selected current ``delta(hK)`` vanish; it is audited only as
    an obstruction, not used for the operational preparation.
    """
    if mass_squared_interval.lower <= 0:
        raise ValueError("positive-energy preparation requires positive mass squared")
    physical = evaluate_physical_massive_advanced_cauchy_pair_at_support_left(
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
    value = [_complex_from_serialized(entry) for entry in physical["physical_two_form_value"]]
    time_derivative = [
        _complex_from_serialized(entry)
        for entry in physical["physical_two_form_time_derivative"]
    ]
    n = two_j + 1
    if len(value) != 6 * n or len(time_derivative) != 6 * n:
        raise ValueError("physical spacetime two-form jet has the wrong dimension")
    alpha, beta = value[: 3 * n], value[3 * n :]
    beta_t = time_derivative[3 * n :]
    d1 = _interval_matrix(d_matrix(two_j, 1), radical_bits)
    d1_adj = _adjoint(d1)
    covector_q = beta
    covector_p = _add(beta_t, [-entry for entry in _matrix_vector(d1, alpha)])

    inverse_mass = RationalInterval(
        Fraction(1, 1) / mass_squared_interval.upper,
        Fraction(1, 1) / mass_squared_interval.lower,
    )
    d_delta = _matrix_vector(d1, _matrix_vector(d1_adj, covector_p))
    a_p = _add(covector_p, _scale_real_interval(d_delta, inverse_mass))
    d2 = _interval_matrix(d_matrix(two_j, 2), radical_bits)
    d2_adj = _adjoint(d2)
    delta_d_q = _matrix_vector(d2_adj, _matrix_vector(d2, covector_q))
    preparation_q = [-entry for entry in a_p]
    preparation_p = _add(delta_d_q, _scale_real_interval(covector_q, mass_squared_interval))
    projector_audit = coclosed_two_form_projector_audit(two_j)
    if any(
        projector_audit[name]
        for name in (
            "idempotence_defect_count",
            "self_adjoint_defect_count",
            "coderivative_defect_count",
            "exact_form_annihilation_defect_count",
            "temporal_component_reconstruction_defect_count",
            "clock_switched_observer_current_defect_count",
        )
    ):
        raise AssertionError("exact co-closed two-form projector audit failed")
    return {
        "detector": detector,
        "two_j": two_j,
        "column": column,
        "mass_squared_interval": mass_squared_interval.serialize(),
        "support_left_physical_time": physical["support_left_physical_time"],
        "canonical_trace": {
            "spacetime_split": "K=dt wedge alpha+beta",
            "canonical_spatial_pair": "q=beta; p=partial_t beta-dSigma alpha",
            "pair_order": ["q", "p"],
            "positive_energy_operators": "A=I+m^-2 dSigma deltaSigma; L=deltaSigma dSigma+m^2",
            "temporal_reconstruction": "alpha=m^-2 deltaSigma p",
            "coclosed_restriction_obstruction": "deltaSigma q=deltaSigma p=0 implies alpha=0 and delta(hK)=0 for a clock-only switch h",
            "coclosed_projector_audit": projector_audit,
        },
        "coupling_stripped_advanced_covector_q": [
            entry.serialize() for entry in covector_q
        ],
        "coupling_stripped_advanced_covector_p": [
            entry.serialize() for entry in covector_p
        ],
        "coupling_stripped_preparation_q": [
            entry.serialize() for entry in preparation_q
        ],
        "coupling_stripped_preparation_p": [
            entry.serialize() for entry in preparation_p
        ],
        "coupling_stripped_preparation_order": ["tilde_q_u=-(I+m^-2 dSigma deltaSigma)tilde_p_v", "tilde_p_u=(deltaSigma dSigma+m_squared)tilde_q_v"],
        "claim_boundary": "finite unrestricted canonical trace and coupling-stripped positive-energy dual through two_j=4 for a runtime positive mass interval; the co-closed restricted dual is a certified zero-source obstruction, while coefficient nonvanishing, infinite spatial tail, free evolution and I_abc remain open",
    }
