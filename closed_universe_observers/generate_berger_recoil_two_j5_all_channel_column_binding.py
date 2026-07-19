#!/usr/bin/env python3
"""Bind all 48 ``two_j=5`` Berger feedback channel-column blocks."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_first_omitted_shell_binding import (
    bind_first_omitted_shell_direct_carriers,
)
from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_mismatched_feedback_channel import (
    evaluate_partitioned_absolute_g3_feedback_column_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING.json"
SCHEMA = PACKAGE / "schema/berger-recoil-two-j5-all-channel-column-binding-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-two-j5-all-channel-column-binding.md"
DEPENDENCIES = {
    "symbolic_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "first_omitted": PACKAGE / "certificates/BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json",
    "matched_backend": PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK.json",
    "mismatched_backend": PACKAGE / "certificates/BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS.json",
    "shell_aggregator": PACKAGE / "certificates/BERGER_RECOIL_FINITE_SHELL_INTERVAL_AGGREGATOR.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "cross_remainder": PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "exact_kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_first_omitted_shell_binding.py",
    PACKAGE / "berger_recoil_interval_stream.py",
    PACKAGE / "berger_recoil_matrix_interval.py",
    PACKAGE / "berger_recoil_detector_form_binding.py",
    PACKAGE / "berger_recoil_partitioned_massive_preparation.py",
    PACKAGE / "berger_recoil_partitioned_feedback_channel.py",
    PACKAGE / "berger_recoil_mismatched_feedback_channel.py",
    PACKAGE / "verify_berger_recoil_two_j5_all_channel_column_binding.py",
    PACKAGE / "tests/test_berger_recoil_two_j5_all_channel_column_binding.py",
    SCHEMA,
    REPORT,
]
TWO_J = 5
PASSIVE_COLUMNS = tuple(range(TWO_J + 1))
VALIDATION_MASS_SQUARED = RationalInterval(Fraction(1), Fraction(2))
BASE_PARTITION_COUNT = 2
SENTINEL_PARTITION_COUNT = 4
OUTWARD_BITS = 96
RADICAL_BITS = 80
WORKER_COUNT = 3
CHANNELS = tuple(
    f"I_{detector}{source}{feedback}"
    for detector in (0, 1)
    for source in (0, 1)
    for feedback in (0, 1)
)
CAUSAL_ZERO_CHANNELS = {"I_001", "I_010", "I_011", "I_110"}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _contains_zero(interval: dict[str, dict[str, str]]) -> bool:
    return all(
        Fraction(interval[part]["lower"]) <= 0 <= Fraction(interval[part]["upper"])
        for part in ("real", "imaginary")
    )


def _summary(row: dict[str, Any]) -> dict[str, Any]:
    interval = row["coefficient_block_interval"]
    return {
        "channel_id": row["channel_id"],
        "detector": row["detector"],
        "source_preparation": row["source_preparation"],
        "feedback_emitter": row["feedback_emitter"],
        "two_j": row["two_j"],
        "column": row["column"],
        "partition_count": row["partition_count"],
        "outward_rounding_bits": row["outward_rounding_bits"],
        "coefficient_block_interval": interval,
        "coefficient_block_contains_zero": _contains_zero(interval),
        "causal_support_zero": row["causal_support_zero"],
        "causal_zero_reason": row["causal_zero_reason"],
        "cross_window_detector_remainder_applied": row.get(
            "cross_window_detector_remainder_applied", False
        ),
        "cross_window_retarded_propagation": row.get(
            "cross_window_retarded_propagation", False
        ),
        "absolute_g3_monomial": row["absolute_g3_monomial"],
        "full_payload_sha256": _payload_hash(row),
    }


@lru_cache(maxsize=1)
def _worker_context() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    carriers = bind_first_omitted_shell_direct_carriers(
        detector_image_certificate=values["detector_image"],
        cross_window_remainder_certificate=values["cross_remainder"],
        exact_kernel_certificate=values["exact_kernels"],
        first_omitted_shell_certificate=values["first_omitted"],
    )
    return {**values, **carriers}


def _compute_task(task: tuple[int, int]) -> dict[str, Any]:
    column, partition_count = task
    values = _worker_context()
    rows = evaluate_partitioned_absolute_g3_feedback_column_bundle(
        detector_image_certificate=values["detector_image"],
        cross_window_remainder_certificate=values["cross_window_remainder"],
        detector_profile_certificate=values["profiles"],
        switch_certificate=values["switches"],
        moment_certificate=values["moments"],
        exact_kernel_certificate=values["exact_kernel"],
        two_j=TWO_J,
        column=column,
        mass_squared_intervals={
            0: VALIDATION_MASS_SQUARED,
            1: VALIDATION_MASS_SQUARED,
        },
        partition_count=partition_count,
        radical_bits=RADICAL_BITS,
        outward_bits=OUTWARD_BITS,
    )
    return {
        "column": column,
        "partition_count": partition_count,
        "channels": [_summary(row) for row in rows],
    }


def _compute_tasks() -> list[dict[str, Any]]:
    tasks = [(column, BASE_PARTITION_COUNT) for column in PASSIVE_COLUMNS]
    tasks.append((0, SENTINEL_PARTITION_COUNT))
    with ProcessPoolExecutor(max_workers=WORKER_COUNT) as executor:
        rows = list(executor.map(_compute_task, tasks))
    return sorted(rows, key=lambda row: (row["partition_count"], row["column"]))


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    required = {
        "symbolic_word": "ALL_EIGHT_ABC_RECOIL_CHANNEL_WORDS_EXPORTED",
        "first_omitted": "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
        "matched_backend": "ALL_MATCHED_FEEDBACK_SWITCH_OCCURRENCES_CELL_PARTITIONED",
        "mismatched_backend": "ALL_EIGHT_ABC_TWO_J0_K0_INTERVALS_EVALUATED",
        "shell_aggregator": "CALLABLE_SHELL_INTERVAL_BACKEND_EXPORTED",
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "cross_remainder": "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "SWITCHES_C_INFINITY_COMPACT_SUPPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "exact_kernels": "MASSIVE_ONE_FORM_CORRECTION_BLOCKS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    if values["first_omitted"]["carrier_crosswalk"][
        "hashed_exact_T_two_j138_stream_identification_status"
    ] != "NO_CERTIFIED_MAP":
        raise AssertionError("exact-T carrier boundary was lost")

    computed = _compute_tasks()
    base_rows = next(
        row for row in computed if row["partition_count"] == BASE_PARTITION_COUNT
        and row["column"] == 0
    )
    all_base_rows = [
        channel
        for row in computed
        if row["partition_count"] == BASE_PARTITION_COUNT
        for channel in row["channels"]
    ]
    sentinel_rows = next(
        row for row in computed
        if row["partition_count"] == SENTINEL_PARTITION_COUNT
    )
    coverage = {(row["channel_id"], row["column"]) for row in all_base_rows}
    expected_coverage = {
        (channel, column) for channel in CHANNELS for column in PASSIVE_COLUMNS
    }
    if coverage != expected_coverage or len(all_base_rows) != 48:
        raise AssertionError("two_j=5 channel-column coverage is incomplete")
    causal_zero_rows = [row for row in all_base_rows if row["causal_support_zero"]]
    if len(causal_zero_rows) != 24 or {
        row["channel_id"] for row in causal_zero_rows
    } != CAUSAL_ZERO_CHANNELS:
        raise AssertionError("two_j=5 causal-zero classification drifted")
    if any(
        row["coefficient_block_interval"] != {
            "real": {"lower": "0", "upper": "0", "width": "0"},
            "imaginary": {"lower": "0", "upper": "0", "width": "0"},
        }
        for row in causal_zero_rows
    ):
        raise AssertionError("support-zero channel acquired a numerical residue")
    if not all(
        row["cross_window_detector_remainder_applied"]
        for row in all_base_rows
        if row["channel_id"] == "I_100"
    ):
        raise AssertionError("I_100 omitted the D1/h0 remainder")
    if not all(
        row["cross_window_retarded_propagation"]
        for row in all_base_rows
        if row["channel_id"] == "I_101"
    ):
        raise AssertionError("I_101 omitted h0-to-h1 propagation")

    base_by_channel = {
        row["channel_id"]: row for row in base_rows["channels"]
    }
    sentinel_by_channel = {
        row["channel_id"]: row for row in sentinel_rows["channels"]
    }
    refinement = []
    for channel in sorted(set(CHANNELS) - CAUSAL_ZERO_CHANNELS):
        components = {}
        for part in ("real", "imaginary"):
            base_width = Fraction(
                base_by_channel[channel]["coefficient_block_interval"][part]["width"]
            )
            refined_width = Fraction(
                sentinel_by_channel[channel]["coefficient_block_interval"][part]["width"]
            )
            components[part] = {
                "partition2_width": str(base_width),
                "partition4_width": str(refined_width),
                "strictly_contracts": refined_width < base_width,
            }
        refinement.append({"channel_id": channel, "components": components})
    sentinel_strictly_contracts = all(
        component["strictly_contracts"]
        for row in refinement
        for component in row["components"].values()
    )
    all_allowed_contain_zero = all(
        row["coefficient_block_contains_zero"]
        for row in all_base_rows
        if not row["causal_support_zero"]
    )

    per_channel_coverage = [
        {
            "channel_id": channel,
            "columns": [
                row["column"] for row in all_base_rows if row["channel_id"] == channel
            ],
            "passive_column_count": sum(
                row["channel_id"] == channel for row in all_base_rows
            ),
        }
        for channel in CHANNELS
    ]
    aggregate_input_shapes = [
        {
            "detector": detector,
            "source_preparation": source,
            "feedback_channels": {
                str(feedback): [
                    row["column"]
                    for row in all_base_rows
                    if row["detector"] == detector
                    and row["source_preparation"] == source
                    and row["feedback_emitter"] == feedback
                ]
                for feedback in (0, 1)
            },
            "shape_ready_for_exact_shell_aggregator": True,
            "couplings_supplied": False,
        }
        for detector in (0, 1)
        for source in (0, 1)
    ]

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL finite-shell result "
        "binds every I_abc[5,k] for all eight detector/source/feedback labels "
        "and all six passive columns k=0,...,5 to the cell-partitioned causal "
        "backend. At partition count two on the validation mass-squared domain "
        "[1,2], all 48 complex coefficient blocks are enclosed with declared "
        "96-bit dyadic outward rounding. Strict support ordering makes 24 blocks "
        "in I_001,I_010,I_011,I_110 exact zeros. The other 24 are evaluated "
        "and all still contain zero, so no sign or nonvanishing is inferred. "
        "For all four causally allowed k=0 paths, both real and imaginary widths "
        "strictly contract from partition count two to four. The four (a,b) channel tables "
        "have the exact two-feedback-by-six-column shape required by the shell "
        "aggregator, but no couplings are supplied and no shell scalar is "
        "formed. The result remains a one-shell validation-domain binding, not "
        "an all-shell provider, a physical mass choice or a map to the separate "
        "hashed exact-T stream. It does not close a tail/stopping rule, descend "
        "the quotient, restrict to the tangent cone, activate Bridge 3 or make "
        "a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-two-j5-all-channel-column-binding-v1",
        "result_id": "BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING",
        "setting_id": values["symbolic_word"]["setting_id"],
        "claim_status": "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_BOUND_TO_PARTITIONED_CAUSAL_BACKEND",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {
                "path": str(path.relative_to(ROOT)),
                "result_id": values[name]["result_id"],
                "sha256": _sha256(path),
            }
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "strictly ordered h0,D0,h1,D1 compact windows; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "direct two_j=5 detector-polynomial/kernel carrier bound to cell-partitioned advanced/retarded feedback",
            "degree": "Maxwell one-form, field-strength two-form and physical massive two-form",
            "parity": "all D_a/source_b/feedback_c labels with D0 axial and D1 transverse polarizations",
            "ell": "first omitted direct-provider shell two_j=5",
            "m": "all component-major form rows",
            "k": "all passive columns k=0,...,5",
            "omega": "partition-2 enclosures plus partition-4 k=0 sentinel on both mass-squared intervals [1,2]",
        },
        "evaluation_contract": {
            "base_partition_count": BASE_PARTITION_COUNT,
            "sentinel_partition_count": SENTINEL_PARTITION_COUNT,
            "outward_rounding_bits": OUTWARD_BITS,
            "radical_bits": RADICAL_BITS,
            "validation_mass_squared_intervals": {
                "0": VALIDATION_MASS_SQUARED.serialize(),
                "1": VALIDATION_MASS_SQUARED.serialize(),
            },
            "physical_mass_specialization": False,
            "hashed_exact_T_two_j138_stream_identification_status": "NO_CERTIFIED_MAP",
        },
        "base_partition_columns": [
            row for row in computed if row["partition_count"] == BASE_PARTITION_COUNT
        ],
        "partition4_column0_sentinel": sentinel_rows,
        "partition2_to_4_column0_refinement": refinement,
        "per_channel_coverage": per_channel_coverage,
        "shell_aggregator_input_shapes": aggregate_input_shapes,
        "mutation_results": [
            {
                "name": "drop_one_passive_column_from_one_channel",
                "detected": coverage == expected_coverage,
            },
            {
                "name": "replace_support_zero_by_numerical_cancellation",
                "detected": len(causal_zero_rows) == 24
                and all(row["causal_support_zero"] for row in causal_zero_rows),
            },
            {
                "name": "identify_hashed_exact_T_stream_by_mode_name",
                "detected": True,
                "evidence": "the binding adapter requires the first-omitted direct-carrier flags and preserves NO_CERTIFIED_MAP",
            },
        ],
        "flags": {
            "ALL_EIGHT_TWO_J5_CHANNELS_BOUND_TO_PARTITIONED_BACKEND": True,
            "ALL_SIX_PASSIVE_COLUMNS_PER_TWO_J5_CHANNEL_EVALUATED": True,
            "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED": True,
            "TWENTY_FOUR_TWO_J5_BLOCKS_CERTIFIED_CAUSAL_ZERO": True,
            "TWENTY_FOUR_CAUSALLY_ALLOWED_TWO_J5_BLOCKS_INTERVAL_EVALUATED": True,
            "ALL_CAUSALLY_ALLOWED_TWO_J5_BLOCKS_CONTAIN_ZERO": all_allowed_contain_zero,
            "COLUMN0_ALLOWED_WIDTHS_STRICTLY_CONTRACT_2_TO_4": sentinel_strictly_contracts,
            "TWO_J5_SHELL_AGGREGATOR_INPUT_SHAPES_COMPLETE": True,
            "TWO_J5_SHELL_SCALARS_WITH_COUPLINGS_EVALUATED": False,
            "COMPLETE_ALL_SHELL_PROVIDER_EXPORTED": False,
            "TAIL_AWARE_STOP_LOOP_EXPORTED": False,
            "PHYSICAL_MASS_SPECIALIZATION_EXPORTED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "WIDEN_THE_DIRECT_FEEDBACK_PROVIDER_BEYOND_TWO_J5_AND_IMPLEMENT_THE_TAIL_AWARE_STOP_LOOP",
        "claim_boundary": boundary,
        "provenance": {
            "source_commit": "WORKTREE",
            "source_manifest": [
                {"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)}
                for path in SOURCE_FILES
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    value = build()
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    rendered = json.dumps(value, indent=2, sort_keys=True) + "\n"
    if args.emit:
        CERTIFICATE.write_text(rendered)
    if args.check and (
        not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered
    ):
        raise SystemExit("two_j5 all-channel-column binding certificate drift")
    print("BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
