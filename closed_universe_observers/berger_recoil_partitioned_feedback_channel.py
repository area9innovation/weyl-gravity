"""Cell-partitioned detector-matched Berger feedback contractions."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Mapping, Sequence

from closed_universe_observers.berger_recoil_detector_form_binding import (
    _cached_interval_d_matrix,
    apply_spacetime_dhat1_to_detector_advanced_maxwell,
)
from closed_universe_observers.berger_recoil_free_emitter_retarded_channel import (
    _identity_matrix,
    _matrix_add,
    _matrix_multiply,
    _scale_matrix_diagonal,
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
    _detector_center_physical_time,
    _switch_support,
    _translate_vector_polynomial,
)
from closed_universe_observers.berger_recoil_matched_feedback_channel import (
    _complex_from_serialized,
    _conjugate,
    _deserialize_polynomial,
    _matrix_vector,
    _zero_vector,
)
from closed_universe_observers.berger_recoil_matrix_interval import (
    kernel_stage_from_sine_enclosure,
    round_kernel_stage_outward,
)
from closed_universe_observers.berger_recoil_partitioned_massive_preparation import (
    evaluate_partitioned_positive_energy_preparation_at_support_left,
)
from closed_universe_observers.berger_recoil_switch_intervals import (
    emitter_switch_interval,
)
Vector = Sequence[ComplexRationalInterval]
Matrix = Sequence[Sequence[ComplexRationalInterval]]


def _round_vector_outward(
    vector: Vector, bits: int | None
) -> list[ComplexRationalInterval]:
    return (
        [entry.round_outward(bits) for entry in vector]
        if bits is not None
        else list(vector)
    )


def _round_matrix_outward(
    matrix: Matrix, bits: int | None
) -> list[list[ComplexRationalInterval]]:
    return (
        [[entry.round_outward(bits) for entry in row] for row in matrix]
        if bits is not None
        else [list(row) for row in matrix]
    )


def _real_multiplier(value: RationalInterval) -> ComplexRationalInterval:
    return ComplexRationalInterval(value, RationalInterval.point(0))


def _interval_power(value: RationalInterval, exponent: int) -> RationalInterval:
    if exponent < 0:
        raise ValueError("interval exponent must be nonnegative")
    result = RationalInterval.point(1)
    factor = value
    power = exponent
    while power:
        if power & 1:
            result = result * factor
        factor = factor * factor
        power >>= 1
    return result


def _vector_add(*vectors: Vector) -> list[ComplexRationalInterval]:
    if not vectors or any(len(vector) != len(vectors[0]) for vector in vectors):
        raise ValueError("vector dimensions must agree")
    return [
        sum(
            (vector[row] for vector in vectors),
            ComplexRationalInterval.point(),
        )
        for row in range(len(vectors[0]))
    ]


def _vector_scale_real(
    vector: Vector, scalar: RationalInterval
) -> list[ComplexRationalInterval]:
    multiplier = _real_multiplier(scalar)
    return [entry * multiplier for entry in vector]


def _vector_norm_upper(vector: Vector) -> Fraction:
    return max((entry.absolute_upper() for entry in vector), default=Fraction(0))


def _add_box(vector: Vector, radius: Fraction) -> list[ComplexRationalInterval]:
    radius = Fraction(radius)
    if radius < 0:
        raise ValueError("box radius must be nonnegative")
    box = RationalInterval(-radius, radius)
    return [
        ComplexRationalInterval(entry.real + box, entry.imaginary + box)
        for entry in vector
    ]


def _evaluate_vector_polynomial_on_cell(
    coefficients: Sequence[Vector],
    remainder_upper: Fraction,
    coordinate: RationalInterval,
    outward_bits: int | None = None,
) -> list[ComplexRationalInterval]:
    if not coefficients or not coefficients[0]:
        raise ValueError("vector polynomial must be nonempty")
    dimension = len(coefficients[0])
    if any(len(vector) != dimension for vector in coefficients):
        raise ValueError("vector polynomial dimensions must agree")
    output = _zero_vector(dimension)
    for power, vector in enumerate(coefficients):
        multiplier = _real_multiplier(_interval_power(coordinate, power))
        output = _vector_add(
            output,
            [entry * multiplier for entry in vector],
        )
        output = _round_vector_outward(output, outward_bits)
    return _round_vector_outward(
        _add_box(output, Fraction(remainder_upper)), outward_bits
    )


def _evaluate_kernel_polynomial_on_cell(
    stage: Mapping[str, Any],
    coordinate: RationalInterval,
    outward_bits: int | None = None,
) -> list[list[ComplexRationalInterval]]:
    matrices = stage["coefficient_matrices"]
    if not matrices or not matrices[0]:
        raise ValueError("kernel polynomial must be nonempty")
    dimension = len(matrices[0])
    output = [
        [ComplexRationalInterval.point() for _ in range(dimension)]
        for _ in range(dimension)
    ]
    for power, matrix in enumerate(matrices):
        if len(matrix) != dimension or any(len(row) != dimension for row in matrix):
            raise ValueError("kernel matrices must be square")
        multiplier = _real_multiplier(_interval_power(coordinate, power))
        output = [
            [
                output[row][column] + matrix[row][column] * multiplier
                for column in range(dimension)
            ]
            for row in range(dimension)
        ]
        output = _round_matrix_outward(output, outward_bits)
    return output


def _kernel_action_on_cell(
    stage: Mapping[str, Any],
    coordinate: RationalInterval,
    source: Vector,
    outward_bits: int | None = None,
) -> list[ComplexRationalInterval]:
    matrix = _evaluate_kernel_polynomial_on_cell(
        stage, coordinate, outward_bits=outward_bits
    )
    output = _round_vector_outward(_matrix_vector(matrix, source), outward_bits)
    kernel_remainder = Fraction(stage["uniform_remainder_upper"])
    return _round_vector_outward(
        _add_box(output, kernel_remainder * _vector_norm_upper(source)),
        outward_bits,
    )


def _causal_convolution_cell_enclosures(
    *,
    source_cells: Sequence[Vector],
    kernel_stage: Mapping[str, Any],
    cell_width: Fraction,
    orientation: str,
    outward_bits: int | None = None,
) -> list[list[ComplexRationalInterval]]:
    """Uniformly enclose a Volterra convolution on every output cell.

    Full source cells are integrated with their exact width.  The one
    triangular source/output cell is enclosed with a variable length in
    ``[0,cell_width]``.  This deliberately over-encloses the diagonal triangle
    but its loss contracts under refinement.
    """
    if orientation not in ("retarded", "advanced"):
        raise ValueError("orientation must be retarded or advanced")
    if not source_cells or not source_cells[0]:
        raise ValueError("source cells must be nonempty")
    dimension = len(source_cells[0])
    if any(len(vector) != dimension for vector in source_cells):
        raise ValueError("source cell dimensions must agree")
    width = Fraction(cell_width)
    if width <= 0:
        raise ValueError("cell width must be positive")
    output = []
    for target in range(len(source_cells)):
        value = _zero_vector(dimension)
        source_indices = (
            range(0, target + 1)
            if orientation == "retarded"
            else range(target, len(source_cells))
        )
        for source_index in source_indices:
            separation = abs(target - source_index)
            if source_index == target:
                tau = RationalInterval(Fraction(0), width)
                integration_length = RationalInterval(Fraction(0), width)
            else:
                tau = RationalInterval(
                    Fraction(max(0, separation - 1)) * width,
                    Fraction(separation + 1) * width,
                )
                integration_length = RationalInterval.point(width)
            integrand = _kernel_action_on_cell(
                kernel_stage,
                tau,
                source_cells[source_index],
                outward_bits=outward_bits,
            )
            value = _vector_add(
                value,
                _vector_scale_real(integrand, integration_length),
            )
            value = _round_vector_outward(value, outward_bits)
        output.append(value)
    return output


def _switch_cell_data(
    *,
    switch_certificate: Mapping[str, Any],
    moment_certificate: Mapping[str, Any],
    switch_id: str,
    support_left: Fraction,
    cell_width: Fraction,
    partition_count: int,
) -> list[dict[str, RationalInterval]]:
    rows = []
    for index in range(partition_count):
        physical_cell = RationalInterval(
            support_left + index * cell_width,
            support_left + (index + 1) * cell_width,
        )
        switch = emitter_switch_interval(
            switch_certificate,
            moment_certificate,
            switch_id=switch_id,
            physical_time_interval=physical_cell,
        )
        rows.append(
            {
                "value": RationalInterval.from_serialized(switch["value"]),
                "derivative": RationalInterval.from_serialized(
                    switch["physical_time_derivative"]
                ),
            }
        )
    return rows


def _kernel_stages(
    *,
    exact_kernel_certificate: Mapping[str, Any],
    two_j: int,
    family: str,
    degrees: Sequence[int],
    mass_squared_interval: RationalInterval,
    slab_length: Fraction,
    radical_bits: int,
    label_prefix: str,
    outward_bits: int | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    enclosures = {
        degree: enclose_exact_mode_sine_kernel(
            exact_kernel_certificate,
            two_j=two_j,
            family=family,
            form_degree=degree,
            mass_squared_interval=mass_squared_interval,
            slab_length=slab_length,
            radical_bits=radical_bits,
        )
        for degree in degrees
    }
    sine = {
        degree: kernel_stage_from_sine_enclosure(enclosures[degree])
        for degree in degrees
    }
    cosine = {
        degree: _cosine_stage_from_sine_stage(sine[degree], enclosures[degree])
        for degree in degrees
    }
    if outward_bits is not None:
        sine = {
            degree: round_kernel_stage_outward(stage, outward_bits)
            for degree, stage in sine.items()
        }
        cosine = {
            degree: round_kernel_stage_outward(stage, outward_bits)
            for degree, stage in cosine.items()
        }
    if len(degrees) != 2:
        raise ValueError("spacetime block construction requires two degrees")
    return (
        _block_diagonal_kernel_stage(
            sine[degrees[0]],
            sine[degrees[1]],
            label=f"{label_prefix}_sine",
        ),
        _block_diagonal_kernel_stage(
            cosine[degrees[0]],
            cosine[degrees[1]],
            label=f"{label_prefix}_cosine",
        ),
    )


def _spacetime_d_one_form_cells(
    *,
    field_cells: Sequence[Vector],
    time_derivative_cells: Sequence[Vector],
    two_j: int,
    radical_bits: int,
    outward_bits: int | None = None,
) -> list[list[ComplexRationalInterval]]:
    n = two_j + 1
    if len(field_cells) != len(time_derivative_cells) or any(
        len(field) != 4 * n or len(derivative) != 4 * n
        for field, derivative in zip(field_cells, time_derivative_cells)
    ):
        raise ValueError("Maxwell cell dimensions do not agree")
    d0 = _cached_interval_d_matrix(two_j, 0, radical_bits)
    d1 = _cached_interval_d_matrix(two_j, 1, radical_bits)
    output = []
    for field, derivative in zip(field_cells, time_derivative_cells):
        phi, spatial = field[:n], field[n:]
        spatial_t = derivative[n:]
        output.append(_round_vector_outward(
            _vector_add(spatial_t, [-entry for entry in _matrix_vector(d0, phi)])
            + _matrix_vector(d1, spatial),
            outward_bits,
        ))
    return output


def _advanced_physical_emitter_cells(
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
    radical_bits: int,
    outward_bits: int | None = None,
) -> dict[str, object]:
    switch_id = {"D0": "h_0", "D1": "h_1"}[detector]
    support_left, support_right = _switch_support(switch_certificate, switch_id)
    length = support_right - support_left
    width = length / partition_count
    switch_cells = _switch_cell_data(
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        switch_id=switch_id,
        support_left=support_left,
        cell_width=width,
        partition_count=partition_count,
    )
    detector_source = apply_spacetime_dhat1_to_detector_advanced_maxwell(
        detector_image_certificate,
        detector=detector,
        two_j=two_j,
        column=column,
        radical_bits=radical_bits,
    )
    center = _detector_center_physical_time(
        detector_profile_certificate, detector
    )
    source_in_y = _translate_vector_polynomial(
        _deserialize_polynomial(detector_source["polynomial_coefficients"]),
        center - support_right,
    )
    source_remainder = Fraction(
        detector_source["remainder_audit"][
            "uniform_output_vector_remainder_upper"
        ]
    )
    d_advanced_cells = [
        _evaluate_vector_polynomial_on_cell(
            source_in_y,
            source_remainder,
            RationalInterval(
                length - (index + 1) * width,
                length - index * width,
            ),
            outward_bits=outward_bits,
        )
        for index in range(partition_count)
    ]
    switched_two_form_cells = [
        _vector_scale_real(source, switch["value"])
        for source, switch in zip(d_advanced_cells, switch_cells)
    ]
    wave_two_sine, _ = _kernel_stages(
        exact_kernel_certificate=exact_kernel_certificate,
        two_j=two_j,
        family="massive_two_form",
        degrees=(1, 2),
        mass_squared_interval=mass_squared_interval,
        slab_length=length,
        radical_bits=radical_bits,
        label_prefix="massive_two_form_advanced",
        outward_bits=outward_bits,
    )
    wave_two_cells = _causal_convolution_cell_enclosures(
        source_cells=switched_two_form_cells,
        kernel_stage=wave_two_sine,
        cell_width=width,
        orientation="advanced",
        outward_bits=outward_bits,
    )
    n = two_j + 1
    delta_source_cells = [
        _zero_vector(n)
        + _vector_scale_real(source[: 3 * n], switch["derivative"])
        for source, switch in zip(d_advanced_cells, switch_cells)
    ]
    wave_one_sine, wave_one_cosine = _kernel_stages(
        exact_kernel_certificate=exact_kernel_certificate,
        two_j=two_j,
        family="massive_two_form",
        degrees=(0, 1),
        mass_squared_interval=mass_squared_interval,
        slab_length=length,
        radical_bits=radical_bits,
        label_prefix="massive_one_form_advanced",
        outward_bits=outward_bits,
    )
    wave_one_cells = _causal_convolution_cell_enclosures(
        source_cells=delta_source_cells,
        kernel_stage=wave_one_sine,
        cell_width=width,
        orientation="advanced",
        outward_bits=outward_bits,
    )
    # The cosine convolution is d/dx for x=t_right-t, hence physical d/dt=-d/dx.
    wave_one_time_derivative_cells = [
        [-entry for entry in vector]
        for vector in _causal_convolution_cell_enclosures(
            source_cells=delta_source_cells,
            kernel_stage=wave_one_cosine,
            cell_width=width,
            orientation="advanced",
            outward_bits=outward_bits,
        )
    ]
    d_wave_one_cells = _spacetime_d_one_form_cells(
        field_cells=wave_one_cells,
        time_derivative_cells=wave_one_time_derivative_cells,
        two_j=two_j,
        radical_bits=radical_bits,
        outward_bits=outward_bits,
    )
    inverse_mass = RationalInterval(
        Fraction(1) / mass_squared_interval.upper,
        Fraction(1) / mass_squared_interval.lower,
    )
    physical_cells = [
        _round_vector_outward(
            _vector_add(wave_two, _vector_scale_real(d_wave_one, inverse_mass)),
            outward_bits,
        )
        for wave_two, d_wave_one in zip(wave_two_cells, d_wave_one_cells)
    ]
    return {
        "support": (support_left, support_right),
        "cell_width": width,
        "switch_cells": switch_cells,
        "physical_cells": physical_cells,
        "outward_rounding_bits": outward_bits,
    }


def _leading_retarded_field_strength_cells(
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
    radical_bits: int,
    outward_bits: int | None = None,
) -> dict[str, object]:
    preparation = evaluate_partitioned_positive_energy_preparation_at_support_left(
        detector_image_certificate=detector_image_certificate,
        detector_profile_certificate=detector_profile_certificate,
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        exact_kernel_certificate=exact_kernel_certificate,
        detector=detector,
        two_j=two_j,
        column=column,
        mass_squared_interval=mass_squared_interval,
        partition_count=partition_count,
        radical_bits=radical_bits,
        outward_bits=outward_bits,
    )
    q0 = [
        _complex_from_serialized(entry)
        for entry in preparation["coupling_stripped_preparation_q"]
    ]
    p0 = [
        _complex_from_serialized(entry)
        for entry in preparation["coupling_stripped_preparation_p"]
    ]
    q0 = _round_vector_outward(q0, outward_bits)
    p0 = _round_vector_outward(p0, outward_bits)
    n = two_j + 1
    dimension = 3 * n
    if len(q0) != dimension or len(p0) != dimension:
        raise ValueError("partitioned preparation has the wrong dimension")
    support_left, support_right = map(Fraction, preparation["support_physical_time"])
    length = support_right - support_left
    width = length / partition_count
    switch_id = preparation["switch_id"]
    switch_cells = _switch_cell_data(
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        switch_id=switch_id,
        support_left=support_left,
        cell_width=width,
        partition_count=partition_count,
    )
    d1 = _cached_interval_d_matrix(two_j, 1, radical_bits)
    delta_two = _adjoint(d1)
    d2 = _cached_interval_d_matrix(two_j, 2, radical_bits)
    delta_three = _adjoint(d2)
    inverse_mass = RationalInterval(
        Fraction(1) / mass_squared_interval.upper,
        Fraction(1) / mass_squared_interval.lower,
    )
    inverse_mass_complex = _real_multiplier(inverse_mass)
    a_operator = _matrix_add(
        _identity_matrix(dimension),
        [
            [entry * inverse_mass_complex for entry in row]
            for row in _matrix_multiply(d1, delta_two)
        ],
    )
    ell_operator = _scale_matrix_diagonal(
        _matrix_multiply(delta_three, d2), mass_squared_interval
    )
    a_operator = _round_matrix_outward(a_operator, outward_bits)
    ell_operator = _round_matrix_outward(ell_operator, outward_bits)
    a_p0 = _round_vector_outward(_matrix_vector(a_operator, p0), outward_bits)
    ell_q0 = _round_vector_outward(_matrix_vector(ell_operator, q0), outward_bits)
    massive_sine_enclosure = enclose_exact_mode_sine_kernel(
        exact_kernel_certificate,
        two_j=two_j,
        family="massive_two_form",
        form_degree=2,
        mass_squared_interval=mass_squared_interval,
        slab_length=length,
        radical_bits=radical_bits,
    )
    massive_sine = kernel_stage_from_sine_enclosure(massive_sine_enclosure)
    massive_cosine = _cosine_stage_from_sine_stage(
        massive_sine, massive_sine_enclosure
    )
    if outward_bits is not None:
        massive_sine = round_kernel_stage_outward(massive_sine, outward_bits)
        massive_cosine = round_kernel_stage_outward(massive_cosine, outward_bits)
    alpha_cells = []
    for index in range(partition_count):
        time_cell = RationalInterval(index * width, (index + 1) * width)
        p_cell = _round_vector_outward(_vector_add(
            _kernel_action_on_cell(
                massive_cosine, time_cell, p0, outward_bits=outward_bits
            ),
            [
                -entry
                for entry in _kernel_action_on_cell(
                    massive_sine,
                    time_cell,
                    ell_q0,
                    outward_bits=outward_bits,
                )
            ],
        ), outward_bits)
        alpha_cells.append(
            _round_vector_outward(
                _vector_scale_real(_matrix_vector(delta_two, p_cell), inverse_mass),
                outward_bits,
            )
        )
    current_cells = [
        _zero_vector(n)
        + _vector_scale_real(alpha, switch["derivative"])
        for alpha, switch in zip(alpha_cells, switch_cells)
    ]
    maxwell_sine, maxwell_cosine = _kernel_stages(
        exact_kernel_certificate=exact_kernel_certificate,
        two_j=two_j,
        family="Maxwell",
        degrees=(0, 1),
        mass_squared_interval=RationalInterval.point(0),
        slab_length=length,
        radical_bits=radical_bits,
        label_prefix="Maxwell_retarded",
        outward_bits=outward_bits,
    )
    field_cells = _causal_convolution_cell_enclosures(
        source_cells=current_cells,
        kernel_stage=maxwell_sine,
        cell_width=width,
        orientation="retarded",
        outward_bits=outward_bits,
    )
    time_derivative_cells = _causal_convolution_cell_enclosures(
        source_cells=current_cells,
        kernel_stage=maxwell_cosine,
        cell_width=width,
        orientation="retarded",
        outward_bits=outward_bits,
    )
    field_strength_cells = _spacetime_d_one_form_cells(
        field_cells=field_cells,
        time_derivative_cells=time_derivative_cells,
        two_j=two_j,
        radical_bits=radical_bits,
        outward_bits=outward_bits,
    )
    return {
        "support": (support_left, support_right),
        "cell_width": width,
        "switch_cells": switch_cells,
        "field_strength_cells": field_strength_cells,
    }


def _lorentzian_two_form_pairing_cell(
    left: Vector,
    right: Vector,
    temporal_dimension: int,
    outward_bits: int | None = None,
) -> ComplexRationalInterval:
    if len(left) != len(right) or not 0 < temporal_dimension < len(left):
        raise ValueError("two-form pairing dimensions do not agree")
    value = ComplexRationalInterval.point()
    for row, (left_entry, right_entry) in enumerate(zip(left, right)):
        term = _conjugate(left_entry) * right_entry
        value = value + (-term if row < temporal_dimension else term)
        if outward_bits is not None:
            value = value.round_outward(outward_bits)
    return value


def evaluate_partitioned_detector_matched_absolute_g3_feedback_channel(
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
    outward_bits: int | None = None,
) -> dict[str, object]:
    """Enclose ``I_aaa[two_j,column]`` with every switch cellwise."""
    if detector not in ("D0", "D1"):
        raise ValueError("detector must be D0 or D1")
    if mass_squared_interval.lower <= 0:
        raise ValueError("feedback mass squared must be positive")
    if partition_count < 2 or partition_count % 2:
        raise ValueError("partition_count must be an even integer at least two")
    advanced = _advanced_physical_emitter_cells(
        detector_image_certificate=detector_image_certificate,
        detector_profile_certificate=detector_profile_certificate,
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        exact_kernel_certificate=exact_kernel_certificate,
        detector=detector,
        two_j=two_j,
        column=column,
        mass_squared_interval=mass_squared_interval,
        partition_count=partition_count,
        radical_bits=radical_bits,
        outward_bits=outward_bits,
    )
    retarded = _leading_retarded_field_strength_cells(
        detector_image_certificate=detector_image_certificate,
        detector_profile_certificate=detector_profile_certificate,
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        exact_kernel_certificate=exact_kernel_certificate,
        detector=detector,
        two_j=two_j,
        column=column,
        mass_squared_interval=mass_squared_interval,
        partition_count=partition_count,
        radical_bits=radical_bits,
        outward_bits=outward_bits,
    )
    if advanced["support"] != retarded["support"]:
        raise ValueError("advanced and retarded supports disagree")
    if advanced["cell_width"] != retarded["cell_width"]:
        raise ValueError("advanced and retarded partitions disagree")
    width = Fraction(advanced["cell_width"])
    value = ComplexRationalInterval.point()
    cell_rows = []
    for index, (advanced_field, retarded_field, switch) in enumerate(
        zip(
            advanced["physical_cells"],
            retarded["field_strength_cells"],
            advanced["switch_cells"],
        )
    ):
        switched_retarded = _vector_scale_real(retarded_field, switch["value"])
        cell_pairing = _lorentzian_two_form_pairing_cell(
            advanced_field,
            switched_retarded,
            3 * (two_j + 1),
            outward_bits=outward_bits,
        ).scale(width)
        value = value + cell_pairing
        cell_rows.append(
            {
                "cell_index": index,
                "cell_pairing_interval": cell_pairing.serialize(),
                "switch_value": switch["value"].serialize(),
                "switch_derivative": switch["derivative"].serialize(),
            }
        )
    label = "0" if detector == "D0" else "1"
    return {
        "channel_id": f"I_{label}{label}{label}",
        "detector": detector,
        "two_j": two_j,
        "column": column,
        "partition_count": partition_count,
        "outward_rounding_bits": outward_bits,
        "cell_width": str(width),
        "mass_squared_interval": mass_squared_interval.serialize(),
        "support_physical_time": [str(entry) for entry in advanced["support"]],
        "coefficient_block_interval": value.serialize(),
        "cell_pairings": cell_rows,
        "absolute_g3_monomial": f"g_{label}^3",
        "peter_weyl_weight_applied": False,
        "physical_green_identity": "G_E,adv=G_(P2+m2),adv+m^-2 d G_(P1+m2),adv delta",
        "claim_boundary": (
            "one detector-matched finite coefficient block with every h/h-prime "
            "occurrence propagated on a common cell partition; the diagonal "
            "Volterra triangles are rigorously over-enclosed and contract under "
            "refinement; no sign, nonzero, shell-sum, tail or physical-mass claim"
        ),
    }
