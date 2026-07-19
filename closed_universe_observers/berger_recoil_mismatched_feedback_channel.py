"""Cell-partitioned evaluation of all mismatched Berger feedback channels."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from typing import Any, Mapping, Sequence

from closed_universe_observers.berger_recoil_detector_form_binding import (
    _cached_interval_d_matrix,
    apply_spacetime_dhat1_to_detector_advanced_maxwell,
)
from closed_universe_observers.berger_recoil_free_emitter_retarded_channel import (
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
    _cosine_stage_from_sine_stage,
    _detector_center_physical_time,
    _switch_support,
    _translate_vector_polynomial,
)
from closed_universe_observers.berger_recoil_matched_feedback_channel import (
    _complex_from_serialized,
    _deserialize_polynomial,
    _matrix_vector,
    _zero_vector,
)
from closed_universe_observers.berger_recoil_matrix_interval import (
    kernel_stage_from_sine_enclosure,
    round_kernel_stage_outward,
)
from closed_universe_observers.berger_recoil_partitioned_feedback_channel import (
    Vector,
    _advanced_physical_emitter_cells,
    _causal_convolution_cell_enclosures,
    _evaluate_vector_polynomial_on_cell,
    _kernel_action_on_cell,
    _kernel_stages,
    _leading_retarded_field_strength_cells,
    _lorentzian_two_form_pairing_cell,
    _round_matrix_outward,
    _round_vector_outward,
    _spacetime_d_one_form_cells,
    _switch_cell_data,
    _vector_add,
    _vector_scale_real,
)
from closed_universe_observers.berger_recoil_partitioned_massive_preparation import (
    evaluate_partitioned_positive_energy_preparation_at_support_left,
)
def _detector_label(index: int) -> str:
    if index not in (0, 1):
        raise ValueError("detector/source/feedback labels must be zero or one")
    return f"D{index}"


def _switch_id(index: int) -> str:
    if index not in (0, 1):
        raise ValueError("detector/source/feedback labels must be zero or one")
    return f"h_{index}"


def _detector_support(
    detector_profile_certificate: Mapping[str, Any], detector: str
) -> tuple[Fraction, Fraction]:
    row = next(
        row
        for row in detector_profile_certificate["exact_detector_profiles"][
            "detectors"
        ]
        if row["id"] == detector
    )
    return tuple(Fraction(entry) for entry in row["physical_time_support"])


def _cross_window_detector_image(
    detector_image_certificate: Mapping[str, Any],
    cross_window_remainder_certificate: Mapping[str, Any],
    *,
    two_j: int,
) -> dict[str, Any]:
    if not cross_window_remainder_certificate.get("flags", {}).get(
        "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED"
    ):
        raise ValueError("D1/h0 cross-window remainder is not certified")
    replacement = next(
        row["uniform_entire_series_remainders"]
        for row in cross_window_remainder_certificate["mode_remainders"]
        if row["two_j"] == two_j
    )
    output = deepcopy(detector_image_certificate)
    detector = next(row for row in output["detectors"] if row["detector_id"] == "D1")
    mode = next(row for row in detector["modes"] if row["two_j"] == two_j)
    mode["uniform_entire_series_remainders"] = deepcopy(replacement)
    return output


def _cross_advanced_physical_emitter_cells(
    *,
    detector_image_certificate: Mapping[str, Any],
    cross_window_remainder_certificate: Mapping[str, Any],
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    moment_certificate: Mapping[str, Any],
    exact_kernel_certificate: Mapping[str, Any],
    two_j: int,
    column: int,
    mass_squared_interval: RationalInterval,
    partition_count: int,
    radical_bits: int,
    outward_bits: int | None = None,
) -> dict[str, object]:
    """Evaluate the D1 advanced detector image on the earlier h0 window."""
    detector = "D1"
    switch_id = "h_0"
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
    expanded_image = _cross_window_detector_image(
        detector_image_certificate,
        cross_window_remainder_certificate,
        two_j=two_j,
    )
    detector_source = apply_spacetime_dhat1_to_detector_advanced_maxwell(
        expanded_image,
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
        label_prefix="massive_two_form_cross_advanced",
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
        label_prefix="massive_one_form_cross_advanced",
        outward_bits=outward_bits,
    )
    wave_one_cells = _causal_convolution_cell_enclosures(
        source_cells=delta_source_cells,
        kernel_stage=wave_one_sine,
        cell_width=width,
        orientation="advanced",
        outward_bits=outward_bits,
    )
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
    return {
        "support": (support_left, support_right),
        "cell_width": width,
        "switch_cells": switch_cells,
        "physical_cells": [
            _round_vector_outward(
                _vector_add(wave_two, _vector_scale_real(d_wave_one, inverse_mass)),
                outward_bits,
            )
            for wave_two, d_wave_one in zip(wave_two_cells, d_wave_one_cells)
        ],
        "cross_window_remainder_applied": True,
        "outward_rounding_bits": outward_bits,
    }


def _retarded_convolution_on_later_cells(
    *,
    source_cells: Sequence[Vector],
    kernel_stage: Mapping[str, Any],
    source_support: tuple[Fraction, Fraction],
    target_support: tuple[Fraction, Fraction],
    target_partition_count: int,
    outward_bits: int | None = None,
) -> list[list[ComplexRationalInterval]]:
    if not source_support[1] < target_support[0]:
        raise ValueError("cross retarded convolution requires disjoint ordered slabs")
    source_width = (source_support[1] - source_support[0]) / len(source_cells)
    target_width = (target_support[1] - target_support[0]) / target_partition_count
    output = []
    for target_index in range(target_partition_count):
        target_left = target_support[0] + target_index * target_width
        target_right = target_left + target_width
        value = _zero_vector(len(source_cells[0]))
        for source_index, source in enumerate(source_cells):
            source_left = source_support[0] + source_index * source_width
            source_right = source_left + source_width
            tau = RationalInterval(
                target_left - source_right,
                target_right - source_left,
            )
            value = _vector_add(
                value,
                _vector_scale_real(
                    _kernel_action_on_cell(
                        kernel_stage, tau, source, outward_bits=outward_bits
                    ),
                    RationalInterval.point(source_width),
                ),
            )
            value = _round_vector_outward(value, outward_bits)
        output.append(value)
    return output


def _cross_retarded_field_strength_cells(
    *,
    detector_image_certificate: Mapping[str, Any],
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    moment_certificate: Mapping[str, Any],
    exact_kernel_certificate: Mapping[str, Any],
    two_j: int,
    column: int,
    source_mass_squared_interval: RationalInterval,
    partition_count: int,
    radical_bits: int,
    outward_bits: int | None = None,
) -> dict[str, object]:
    """Propagate the h0-selected source to the later h1 feedback window."""
    preparation = evaluate_partitioned_positive_energy_preparation_at_support_left(
        detector_image_certificate=detector_image_certificate,
        detector_profile_certificate=detector_profile_certificate,
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        exact_kernel_certificate=exact_kernel_certificate,
        detector="D0",
        two_j=two_j,
        column=column,
        mass_squared_interval=source_mass_squared_interval,
        partition_count=partition_count,
        radical_bits=radical_bits,
        outward_bits=outward_bits,
    )
    q0 = [_complex_from_serialized(x) for x in preparation["coupling_stripped_preparation_q"]]
    p0 = [_complex_from_serialized(x) for x in preparation["coupling_stripped_preparation_p"]]
    q0 = _round_vector_outward(q0, outward_bits)
    p0 = _round_vector_outward(p0, outward_bits)
    n = two_j + 1
    source_support = tuple(Fraction(x) for x in preparation["support_physical_time"])
    target_support = _switch_support(switch_certificate, "h_1")
    source_width = (source_support[1] - source_support[0]) / partition_count
    target_width = (target_support[1] - target_support[0]) / partition_count
    source_switch_cells = _switch_cell_data(
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        switch_id="h_0",
        support_left=source_support[0],
        cell_width=source_width,
        partition_count=partition_count,
    )
    target_switch_cells = _switch_cell_data(
        switch_certificate=switch_certificate,
        moment_certificate=moment_certificate,
        switch_id="h_1",
        support_left=target_support[0],
        cell_width=target_width,
        partition_count=partition_count,
    )
    d1 = _cached_interval_d_matrix(two_j, 1, radical_bits)
    delta_two = _adjoint(d1)
    d2 = _cached_interval_d_matrix(two_j, 2, radical_bits)
    delta_three = _adjoint(d2)
    inverse_mass = RationalInterval(
        Fraction(1) / source_mass_squared_interval.upper,
        Fraction(1) / source_mass_squared_interval.lower,
    )
    ell_operator = _scale_matrix_diagonal(
        _matrix_multiply(delta_three, d2), source_mass_squared_interval
    )
    ell_operator = _round_matrix_outward(ell_operator, outward_bits)
    ell_q0 = _round_vector_outward(_matrix_vector(ell_operator, q0), outward_bits)
    source_length = source_support[1] - source_support[0]
    massive_sine_enclosure = enclose_exact_mode_sine_kernel(
        exact_kernel_certificate,
        two_j=two_j,
        family="massive_two_form",
        form_degree=2,
        mass_squared_interval=source_mass_squared_interval,
        slab_length=source_length,
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
        time_cell = RationalInterval(index * source_width, (index + 1) * source_width)
        p_cell = _round_vector_outward(
            _vector_add(
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
            ),
            outward_bits,
        )
        alpha_cells.append(
            _vector_scale_real(_matrix_vector(delta_two, p_cell), inverse_mass)
        )
    current_cells = [
        _zero_vector(n)
        + _vector_scale_real(alpha, switch["derivative"])
        for alpha, switch in zip(alpha_cells, source_switch_cells)
    ]
    max_separation = target_support[1] - source_support[0]
    maxwell_sine, maxwell_cosine = _kernel_stages(
        exact_kernel_certificate=exact_kernel_certificate,
        two_j=two_j,
        family="Maxwell",
        degrees=(0, 1),
        mass_squared_interval=RationalInterval.point(0),
        slab_length=max_separation,
        radical_bits=radical_bits,
        label_prefix="Maxwell_cross_retarded",
        outward_bits=outward_bits,
    )
    field_cells = _retarded_convolution_on_later_cells(
        source_cells=current_cells,
        kernel_stage=maxwell_sine,
        source_support=source_support,
        target_support=target_support,
        target_partition_count=partition_count,
        outward_bits=outward_bits,
    )
    derivative_cells = _retarded_convolution_on_later_cells(
        source_cells=current_cells,
        kernel_stage=maxwell_cosine,
        source_support=source_support,
        target_support=target_support,
        target_partition_count=partition_count,
        outward_bits=outward_bits,
    )
    return {
        "support": target_support,
        "cell_width": target_width,
        "switch_cells": target_switch_cells,
        "field_strength_cells": _spacetime_d_one_form_cells(
            field_cells=field_cells,
            time_derivative_cells=derivative_cells,
            two_j=two_j,
            radical_bits=radical_bits,
            outward_bits=outward_bits,
        ),
        "source_support": source_support,
        "cross_window_retarded_propagation": True,
    }


def _causal_zero_reason(
    *,
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    detector: int,
    source_preparation: int,
    feedback_emitter: int,
) -> str | None:
    source_support = _switch_support(switch_certificate, _switch_id(source_preparation))
    feedback_support = _switch_support(switch_certificate, _switch_id(feedback_emitter))
    detector_support = _detector_support(
        detector_profile_certificate, _detector_label(detector)
    )
    if feedback_support[1] < source_support[0]:
        return "FEEDBACK_WINDOW_STRICTLY_BEFORE_SOURCE_WINDOW"
    if detector_support[1] < feedback_support[0]:
        return "DETECTOR_WINDOW_STRICTLY_BEFORE_FEEDBACK_WINDOW"
    return None


def evaluate_partitioned_absolute_g3_feedback_channel(
    *,
    detector_image_certificate: Mapping[str, Any],
    cross_window_remainder_certificate: Mapping[str, Any],
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    moment_certificate: Mapping[str, Any],
    exact_kernel_certificate: Mapping[str, Any],
    detector: int,
    source_preparation: int,
    feedback_emitter: int,
    two_j: int,
    column: int,
    source_mass_squared_interval: RationalInterval,
    feedback_mass_squared_interval: RationalInterval,
    partition_count: int,
    radical_bits: int = 80,
    outward_bits: int | None = None,
) -> dict[str, object]:
    """Evaluate one of the eight ``I_abc`` coefficient blocks."""
    for label in (detector, source_preparation, feedback_emitter):
        _detector_label(label)
    if source_mass_squared_interval.lower <= 0 or feedback_mass_squared_interval.lower <= 0:
        raise ValueError("source and feedback masses squared must be positive")
    channel_id = f"I_{detector}{source_preparation}{feedback_emitter}"
    zero_reason = _causal_zero_reason(
        detector_profile_certificate=detector_profile_certificate,
        switch_certificate=switch_certificate,
        detector=detector,
        source_preparation=source_preparation,
        feedback_emitter=feedback_emitter,
    )
    if zero_reason is not None:
        return {
            "channel_id": channel_id,
            "detector": detector,
            "source_preparation": source_preparation,
            "feedback_emitter": feedback_emitter,
            "two_j": two_j,
            "column": column,
            "partition_count": partition_count,
            "coefficient_block_interval": ComplexRationalInterval.point().serialize(),
            "causal_support_zero": True,
            "causal_zero_reason": zero_reason,
            "absolute_g3_monomial": f"g_{source_preparation} g_{feedback_emitter}^2",
            "peter_weyl_weight_applied": False,
            "claim_boundary": "exact zero from strict causal support ordering; no numerical cancellation used",
        }

    if detector == feedback_emitter:
        advanced = _advanced_physical_emitter_cells(
            detector_image_certificate=detector_image_certificate,
            detector_profile_certificate=detector_profile_certificate,
            switch_certificate=switch_certificate,
            moment_certificate=moment_certificate,
            exact_kernel_certificate=exact_kernel_certificate,
            detector=_detector_label(detector),
            two_j=two_j,
            column=column,
            mass_squared_interval=feedback_mass_squared_interval,
            partition_count=partition_count,
            radical_bits=radical_bits,
            outward_bits=outward_bits,
        )
    elif (detector, feedback_emitter) == (1, 0):
        advanced = _cross_advanced_physical_emitter_cells(
            detector_image_certificate=detector_image_certificate,
            cross_window_remainder_certificate=cross_window_remainder_certificate,
            detector_profile_certificate=detector_profile_certificate,
            switch_certificate=switch_certificate,
            moment_certificate=moment_certificate,
            exact_kernel_certificate=exact_kernel_certificate,
            two_j=two_j,
            column=column,
            mass_squared_interval=feedback_mass_squared_interval,
            partition_count=partition_count,
            radical_bits=radical_bits,
            outward_bits=outward_bits,
        )
    else:
        raise AssertionError("unclassified causally allowed advanced channel")

    if source_preparation == feedback_emitter:
        retarded = _leading_retarded_field_strength_cells(
            detector_image_certificate=detector_image_certificate,
            detector_profile_certificate=detector_profile_certificate,
            switch_certificate=switch_certificate,
            moment_certificate=moment_certificate,
            exact_kernel_certificate=exact_kernel_certificate,
            detector=_detector_label(source_preparation),
            two_j=two_j,
            column=column,
            mass_squared_interval=source_mass_squared_interval,
            partition_count=partition_count,
            radical_bits=radical_bits,
            outward_bits=outward_bits,
        )
    elif (source_preparation, feedback_emitter) == (0, 1):
        retarded = _cross_retarded_field_strength_cells(
            detector_image_certificate=detector_image_certificate,
            detector_profile_certificate=detector_profile_certificate,
            switch_certificate=switch_certificate,
            moment_certificate=moment_certificate,
            exact_kernel_certificate=exact_kernel_certificate,
            two_j=two_j,
            column=column,
            source_mass_squared_interval=source_mass_squared_interval,
            partition_count=partition_count,
            radical_bits=radical_bits,
            outward_bits=outward_bits,
        )
    else:
        raise AssertionError("unclassified causally allowed retarded channel")

    if advanced["support"] != retarded["support"] or advanced["cell_width"] != retarded["cell_width"]:
        raise ValueError("advanced and retarded feedback windows disagree")
    width = Fraction(advanced["cell_width"])
    value = ComplexRationalInterval.point()
    for advanced_field, retarded_field, switch in zip(
        advanced["physical_cells"],
        retarded["field_strength_cells"],
        advanced["switch_cells"],
    ):
        value = value + _lorentzian_two_form_pairing_cell(
            advanced_field,
            _vector_scale_real(retarded_field, switch["value"]),
            3 * (two_j + 1),
            outward_bits=outward_bits,
        ).scale(width)
        if outward_bits is not None:
            value = value.round_outward(outward_bits)
    return {
        "channel_id": channel_id,
        "detector": detector,
        "source_preparation": source_preparation,
        "feedback_emitter": feedback_emitter,
        "two_j": two_j,
        "column": column,
        "partition_count": partition_count,
        "outward_rounding_bits": outward_bits,
        "source_mass_squared_interval": source_mass_squared_interval.serialize(),
        "feedback_mass_squared_interval": feedback_mass_squared_interval.serialize(),
        "support_physical_time": [str(x) for x in advanced["support"]],
        "coefficient_block_interval": value.serialize(),
        "causal_support_zero": False,
        "causal_zero_reason": None,
        "cross_window_detector_remainder_applied": bool(
            advanced.get("cross_window_remainder_applied", False)
        ),
        "cross_window_retarded_propagation": bool(
            retarded.get("cross_window_retarded_propagation", False)
        ),
        "absolute_g3_monomial": f"g_{source_preparation} g_{feedback_emitter}^2",
        "peter_weyl_weight_applied": False,
        "claim_boundary": "one finite cell-partitioned I_abc coefficient block; no shell sum, sign, nonzero or physical-mass claim",
    }


def evaluate_partitioned_absolute_g3_feedback_column_bundle(
    *,
    detector_image_certificate: Mapping[str, Any],
    cross_window_remainder_certificate: Mapping[str, Any],
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    moment_certificate: Mapping[str, Any],
    exact_kernel_certificate: Mapping[str, Any],
    two_j: int,
    column: int,
    mass_squared_intervals: Mapping[int, RationalInterval],
    partition_count: int,
    radical_bits: int = 80,
    outward_bits: int | None = None,
) -> list[dict[str, object]]:
    """Evaluate all eight channels while reusing six causal intermediates."""
    if set(mass_squared_intervals) != {0, 1} or any(
        interval.lower <= 0 for interval in mass_squared_intervals.values()
    ):
        raise ValueError("both emitter mass-squared intervals must be positive")
    common = {
        "detector_image_certificate": detector_image_certificate,
        "detector_profile_certificate": detector_profile_certificate,
        "switch_certificate": switch_certificate,
        "moment_certificate": moment_certificate,
        "exact_kernel_certificate": exact_kernel_certificate,
        "two_j": two_j,
        "column": column,
        "partition_count": partition_count,
        "radical_bits": radical_bits,
        "outward_bits": outward_bits,
    }
    advanced = {
        (0, 0): _advanced_physical_emitter_cells(
            detector="D0",
            mass_squared_interval=mass_squared_intervals[0],
            **common,
        ),
        (1, 0): _cross_advanced_physical_emitter_cells(
            cross_window_remainder_certificate=cross_window_remainder_certificate,
            mass_squared_interval=mass_squared_intervals[0],
            **common,
        ),
        (1, 1): _advanced_physical_emitter_cells(
            detector="D1",
            mass_squared_interval=mass_squared_intervals[1],
            **common,
        ),
    }
    retarded = {
        (0, 0): _leading_retarded_field_strength_cells(
            detector="D0",
            mass_squared_interval=mass_squared_intervals[0],
            **common,
        ),
        (0, 1): _cross_retarded_field_strength_cells(
            source_mass_squared_interval=mass_squared_intervals[0],
            **common,
        ),
        (1, 1): _leading_retarded_field_strength_cells(
            detector="D1",
            mass_squared_interval=mass_squared_intervals[1],
            **common,
        ),
    }

    allowed_paths = {
        (0, 0, 0): (advanced[(0, 0)], retarded[(0, 0)]),
        (1, 0, 0): (advanced[(1, 0)], retarded[(0, 0)]),
        (1, 0, 1): (advanced[(1, 1)], retarded[(0, 1)]),
        (1, 1, 1): (advanced[(1, 1)], retarded[(1, 1)]),
    }
    rows: list[dict[str, object]] = []
    for detector, source, feedback in (
        (0, 0, 0),
        (0, 0, 1),
        (0, 1, 0),
        (0, 1, 1),
        (1, 0, 0),
        (1, 0, 1),
        (1, 1, 0),
        (1, 1, 1),
    ):
        channel_id = f"I_{detector}{source}{feedback}"
        if (detector, source, feedback) not in allowed_paths:
            reason = _causal_zero_reason(
                detector_profile_certificate=detector_profile_certificate,
                switch_certificate=switch_certificate,
                detector=detector,
                source_preparation=source,
                feedback_emitter=feedback,
            )
            if reason is None:
                raise AssertionError(f"{channel_id} lost its causal-zero proof")
            rows.append(
                {
                    "channel_id": channel_id,
                    "detector": detector,
                    "source_preparation": source,
                    "feedback_emitter": feedback,
                    "two_j": two_j,
                    "column": column,
                    "partition_count": partition_count,
                    "outward_rounding_bits": outward_bits,
                    "coefficient_block_interval": ComplexRationalInterval.point().serialize(),
                    "causal_support_zero": True,
                    "causal_zero_reason": reason,
                    "absolute_g3_monomial": f"g_{source} g_{feedback}^2",
                    "peter_weyl_weight_applied": False,
                    "shared_intermediate_bundle": True,
                    "claim_boundary": "exact zero from strict causal support ordering; no numerical cancellation used",
                }
            )
            continue
        advanced_row, retarded_row = allowed_paths[(detector, source, feedback)]
        if (
            advanced_row["support"] != retarded_row["support"]
            or advanced_row["cell_width"] != retarded_row["cell_width"]
        ):
            raise ValueError(f"{channel_id} advanced and retarded windows disagree")
        width = Fraction(advanced_row["cell_width"])
        value = ComplexRationalInterval.point()
        for advanced_field, retarded_field, switch in zip(
            advanced_row["physical_cells"],
            retarded_row["field_strength_cells"],
            advanced_row["switch_cells"],
        ):
            value = value + _lorentzian_two_form_pairing_cell(
                advanced_field,
                _vector_scale_real(retarded_field, switch["value"]),
                3 * (two_j + 1),
                outward_bits=outward_bits,
            ).scale(width)
            if outward_bits is not None:
                value = value.round_outward(outward_bits)
        rows.append(
            {
                "channel_id": channel_id,
                "detector": detector,
                "source_preparation": source,
                "feedback_emitter": feedback,
                "two_j": two_j,
                "column": column,
                "partition_count": partition_count,
                "outward_rounding_bits": outward_bits,
                "source_mass_squared_interval": mass_squared_intervals[source].serialize(),
                "feedback_mass_squared_interval": mass_squared_intervals[feedback].serialize(),
                "support_physical_time": [str(x) for x in advanced_row["support"]],
                "coefficient_block_interval": value.serialize(),
                "causal_support_zero": False,
                "causal_zero_reason": None,
                "cross_window_detector_remainder_applied": (detector, feedback) == (1, 0),
                "cross_window_retarded_propagation": (source, feedback) == (0, 1),
                "absolute_g3_monomial": f"g_{source} g_{feedback}^2",
                "peter_weyl_weight_applied": False,
                "shared_intermediate_bundle": True,
                "claim_boundary": "one finite cell-partitioned I_abc coefficient block from a shared six-intermediate column bundle; no shell sum, sign, nonzero or physical-mass claim",
            }
        )
    return rows
