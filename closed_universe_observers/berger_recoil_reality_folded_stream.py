"""Generic reality-folded direct-shell evaluation and stop-loop integration."""

from __future__ import annotations

from fractions import Fraction
from typing import Any, Callable, Mapping, Sequence

from closed_universe_observers.berger_recoil_direct_finite_shell_provider import (
    build_direct_finite_shell_payload,
)
from closed_universe_observers.berger_recoil_first_omitted_shell_binding import (
    bind_direct_finite_shell_payload,
    certified_direct_max_two_j,
)
from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    evaluate_four_recoil_stream_stop,
    evaluate_recoil_shell_interval,
)
from closed_universe_observers.berger_recoil_mismatched_feedback_channel import (
    evaluate_partitioned_absolute_g3_feedback_column_bundle,
)
from closed_universe_observers.berger_recoil_reality_folded_shell import (
    complete_reality_folded_shell,
)


CarrierBundle = Mapping[str, Mapping[str, Any]]
RepresentativeEvaluator = Callable[
    [int, int, CarrierBundle], Sequence[Mapping[str, Any]]
]
ShellEvaluator = Callable[[int, CarrierBundle], Mapping[str, Any]]
STREAM_KEYS = {(a, b) for a in (0, 1) for b in (0, 1)}
CHANNELS = {
    f"I_{detector}{source}{feedback}"
    for detector in (0, 1)
    for source in (0, 1)
    for feedback in (0, 1)
}


def _validated_representative_rows(
    *, two_j: int, column: int, rows: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    copied = [dict(row) for row in rows]
    if len(copied) != len(CHANNELS) or {
        row.get("channel_id") for row in copied
    } != CHANNELS:
        raise ValueError("representative evaluator did not return all eight channels")
    if any(
        int(row.get("two_j", -1)) != two_j
        or int(row.get("column", -1)) != column
        for row in copied
    ):
        raise ValueError("representative evaluator returned the wrong shell or column")
    return copied


def _carrier_cutoff(carriers: CarrierBundle) -> int:
    if set(carriers) != {
        "detector_image",
        "cross_window_remainder",
        "exact_kernel",
    }:
        raise ValueError("the complete three-carrier direct bundle is required")
    cutoffs = {
        certified_direct_max_two_j(
            carriers["detector_image"], carrier="detector"
        ),
        certified_direct_max_two_j(
            carriers["cross_window_remainder"], carrier="cross_window"
        ),
        certified_direct_max_two_j(carriers["exact_kernel"], carrier="kernel"),
    }
    if len(cutoffs) != 1:
        raise ValueError("direct carrier cutoffs disagree")
    return cutoffs.pop()


def evaluate_reality_folded_feedback_shell(
    *,
    two_j: int,
    carriers: CarrierBundle,
    moment_certificate: Mapping[str, Any],
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    spectral_certificate: Mapping[str, Any],
    mass_squared_intervals: Mapping[int, RationalInterval],
    partition_count: int,
    radical_bits: int,
    outward_bits: int,
    representative_evaluator: RepresentativeEvaluator | None = None,
) -> dict[str, Any]:
    """Build, bind, evaluate and reality-complete one contiguous direct shell."""
    previous = _carrier_cutoff(carriers)
    if not isinstance(two_j, int) or two_j != previous + 1:
        raise ValueError("requested shell must extend the direct carrier contiguously")
    if set(mass_squared_intervals) != {0, 1}:
        raise ValueError("both feedback mass-squared intervals are required")
    if partition_count <= 0 or radical_bits < 8 or outward_bits < 8:
        raise ValueError("invalid partition or interval-precision contract")

    payload = build_direct_finite_shell_payload(
        two_j=two_j,
        detector_base_certificate=carriers["detector_image"],
        cross_window_base_certificate=carriers["cross_window_remainder"],
        kernel_base_certificate=carriers["exact_kernel"],
        moment_certificate=moment_certificate,
        detector_profile_certificate=detector_profile_certificate,
        switch_certificate=switch_certificate,
        spectral_certificate=spectral_certificate,
    )
    bound = bind_direct_finite_shell_payload(
        detector_image_certificate=carriers["detector_image"],
        cross_window_remainder_certificate=carriers["cross_window_remainder"],
        exact_kernel_certificate=carriers["exact_kernel"],
        shell_payload=payload,
    )

    def default_evaluator(
        shell: int, column: int, direct_carriers: CarrierBundle
    ) -> Sequence[Mapping[str, Any]]:
        return evaluate_partitioned_absolute_g3_feedback_column_bundle(
            detector_image_certificate=direct_carriers["detector_image"],
            cross_window_remainder_certificate=direct_carriers[
                "cross_window_remainder"
            ],
            detector_profile_certificate=detector_profile_certificate,
            switch_certificate=switch_certificate,
            moment_certificate=moment_certificate,
            exact_kernel_certificate=direct_carriers["exact_kernel"],
            two_j=shell,
            column=column,
            mass_squared_intervals=mass_squared_intervals,
            partition_count=partition_count,
            radical_bits=radical_bits,
            outward_bits=outward_bits,
        )

    evaluator = representative_evaluator or default_evaluator
    representative_columns = []
    for column in range(two_j // 2 + 1):
        rows = _validated_representative_rows(
            two_j=two_j,
            column=column,
            rows=evaluator(two_j, column, bound),
        )
        representative_columns.append(
            {
                "two_j": two_j,
                "column": column,
                "partition_count": partition_count,
                "channels": rows,
            }
        )

    folded = complete_reality_folded_shell(
        two_j=two_j, representative_columns=representative_columns
    )
    expected_blocks = len(CHANNELS) * (two_j + 1)
    if (
        folded["direct_channel_column_count"]
        + folded["reality_derived_channel_column_count"]
        != expected_blocks
    ):
        raise AssertionError("reality-folded shell coverage is incomplete")
    return {
        "two_j": two_j,
        "previous_carrier_cutoff": previous,
        "direct_shell_payload_sha256": payload["payload_sha256"],
        "representative_columns": list(range(two_j // 2 + 1)),
        "direct_carriers": bound,
        "folded_shell": folded,
        "hashed_exact_T_stream_identification_status": "NO_CERTIFIED_MAP",
    }


def aggregate_reality_folded_shell(
    *,
    folded_shell: Mapping[str, Any],
    couplings: Mapping[int, Fraction],
    inverse_berger_volume: RationalInterval,
) -> dict[str, Any]:
    """Aggregate one certified real shell into its four detector/source entries."""
    if set(couplings) != {0, 1}:
        raise ValueError("both exact validation couplings are required")
    two_j = int(folded_shell.get("two_j", -1))
    completed = folded_shell.get("completed_columns", [])
    completed_columns = [int(bundle.get("column", -1)) for bundle in completed]
    if (
        len(completed) != two_j + 1
        or sorted(completed_columns) != list(range(two_j + 1))
    ):
        raise ValueError("completed shell does not contain every passive column")
    real_sums = {
        row["channel_id"]: row for row in folded_shell.get("real_channel_sums", [])
    }
    if set(real_sums) != CHANNELS:
        raise ValueError("all eight real channel sums are required")
    zero = {"lower": "0", "upper": "0", "width": "0"}
    if any(row.get("imaginary_column_sum") != zero for row in real_sums.values()):
        raise ValueError("shell is not certified real after column summation")

    channel_rows = {
        row["channel_id"]: [] for row in real_sums.values()
    }
    for bundle in completed:
        column = int(bundle.get("column", -1))
        if column < 0 or column > two_j:
            raise ValueError("completed shell contains an invalid passive column")
        if {row.get("channel_id") for row in bundle.get("channels", [])} != CHANNELS:
            raise ValueError("completed shell channel coverage is incomplete")
        for row in bundle["channels"]:
            channel_rows[row["channel_id"]].append(
                (
                    column,
                    RationalInterval.from_serialized(
                        row["coefficient_block_interval"]["real"]
                    ),
                )
            )

    aggregate_rows = []
    shell_intervals: dict[str, dict[str, str]] = {}
    for detector, source in sorted(STREAM_KEYS):
        feedback_columns = {
            feedback: [
                interval
                for _, interval in sorted(
                    channel_rows[f"I_{detector}{source}{feedback}"]
                )
            ]
            for feedback in (0, 1)
        }
        result = evaluate_recoil_shell_interval(
            two_j=two_j,
            detector=detector,
            source_preparation=source,
            source_coupling=Fraction(couplings[source]),
            feedback_couplings={
                feedback: Fraction(couplings[feedback]) for feedback in (0, 1)
            },
            inverse_berger_volume=inverse_berger_volume,
            channel_columns=feedback_columns,
        )
        aggregate_rows.append(result)
        shell_intervals[f"{detector}{source}"] = result["shell_interval"]
    return {
        "two_j": two_j,
        "aggregate_rows": aggregate_rows,
        "shell_intervals": shell_intervals,
        "claim_boundary": "one reality-certified shell aggregated with caller-supplied exact validation couplings and inverse volume; no physical specialization inferred",
    }


def run_reality_folded_shell_stream(
    *,
    two_js: Sequence[int],
    carriers: CarrierBundle,
    moment_certificate: Mapping[str, Any],
    detector_profile_certificate: Mapping[str, Any],
    switch_certificate: Mapping[str, Any],
    spectral_certificate: Mapping[str, Any],
    mass_squared_intervals: Mapping[int, RationalInterval],
    couplings: Mapping[int, Fraction],
    inverse_berger_volume: RationalInterval,
    tail_radii_by_two_j: Mapping[int, Mapping[tuple[int, int], Fraction]],
    goal: Mapping[str, object],
    partition_count: int,
    radical_bits: int,
    outward_bits: int,
    initial_partial_intervals: Mapping[
        tuple[int, int], RationalInterval
    ] | None = None,
    representative_evaluator: RepresentativeEvaluator | None = None,
    shell_evaluator: ShellEvaluator | None = None,
) -> dict[str, Any]:
    """Evaluate a contiguous shell sequence and apply the stop gate after each."""
    declared = [int(value) for value in two_js]
    previous = _carrier_cutoff(carriers)
    expected = list(range(previous + 1, previous + 1 + len(declared)))
    if not declared or declared != expected:
        raise ValueError("declared shells must be nonempty, unique and contiguous")
    if set(mass_squared_intervals) != {0, 1}:
        raise ValueError("both feedback mass-squared intervals are required")
    if set(couplings) != {0, 1}:
        raise ValueError("both exact validation couplings are required")
    if inverse_berger_volume.lower <= 0:
        raise ValueError("inverse Berger volume enclosure must be positive")
    if set(tail_radii_by_two_j) != set(declared):
        raise ValueError("tail radii are required after every declared shell")
    if any(set(tail_radii_by_two_j[shell]) != STREAM_KEYS for shell in declared):
        raise ValueError("all four tail radii are required after every shell")
    if any(
        Fraction(radius) < 0
        for shell in declared
        for radius in tail_radii_by_two_j[shell].values()
    ):
        raise ValueError("tail radii must be nonnegative")
    partials = (
        {key: RationalInterval.point(0) for key in STREAM_KEYS}
        if initial_partial_intervals is None
        else dict(initial_partial_intervals)
    )
    if set(partials) != STREAM_KEYS:
        raise ValueError("all four initial partial intervals are required")

    current: CarrierBundle = carriers
    history = []
    for two_j in declared:
        if shell_evaluator is None:
            evaluated = evaluate_reality_folded_feedback_shell(
                two_j=two_j,
                carriers=current,
                moment_certificate=moment_certificate,
                detector_profile_certificate=detector_profile_certificate,
                switch_certificate=switch_certificate,
                spectral_certificate=spectral_certificate,
                mass_squared_intervals=mass_squared_intervals,
                partition_count=partition_count,
                radical_bits=radical_bits,
                outward_bits=outward_bits,
                representative_evaluator=representative_evaluator,
            )
        else:
            evaluated = dict(shell_evaluator(two_j, current))
            if int(evaluated.get("two_j", -1)) != two_j:
                raise ValueError("shell evaluator returned the wrong shell")
        current = evaluated["direct_carriers"]
        if _carrier_cutoff(current) != two_j:
            raise ValueError("shell evaluator did not advance all direct carriers")
        aggregate = aggregate_reality_folded_shell(
            folded_shell=evaluated["folded_shell"],
            couplings=couplings,
            inverse_berger_volume=inverse_berger_volume,
        )
        for detector, source in STREAM_KEYS:
            partials[(detector, source)] = partials[(detector, source)] + (
                RationalInterval.from_serialized(
                    aggregate["shell_intervals"][f"{detector}{source}"]
                )
            )
        stop = evaluate_four_recoil_stream_stop(
            partial_intervals=partials,
            tail_radii=tail_radii_by_two_j[two_j],
            goal=goal,
        )
        history.append(
            {
                "two_j": two_j,
                "direct_shell_payload_sha256": evaluated.get(
                    "direct_shell_payload_sha256", "INJECTED_TEST_SHELL"
                ),
                "representative_columns": evaluated.get(
                    "representative_columns", list(range(two_j // 2 + 1))
                ),
                "folded_shell": evaluated["folded_shell"],
                "aggregate": aggregate,
                "stop_evaluation": stop,
            }
        )
        if stop["stop"]:
            break

    return {
        "declared_two_js": declared,
        "evaluated_two_js": [row["two_j"] for row in history],
        "stopped": history[-1]["stop_evaluation"]["stop"],
        "stop_two_j": history[-1]["two_j"]
        if history[-1]["stop_evaluation"]["stop"]
        else None,
        "history": history,
        "final_partial_intervals": {
            f"{detector}{source}": partials[(detector, source)].serialize()
            for detector, source in sorted(STREAM_KEYS)
        },
        "direct_carriers": current,
        "hashed_exact_T_stream_identification_status": "NO_CERTIFIED_MAP",
        "claim_boundary": "caller-declared contiguous validation shells with fail-closed stop checks; no physical parameter choice, unbounded stream or recoil claim inferred",
    }
