#!/usr/bin/env python3
"""Bind the complete ``two_j=6`` feedback shell using SU(2) reality folding."""

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

from closed_universe_observers.berger_recoil_direct_finite_shell_provider import (
    build_direct_finite_shell_payload,
)
from closed_universe_observers.berger_recoil_first_omitted_shell_binding import (
    bind_direct_finite_shell_payload,
    bind_first_omitted_shell_direct_carriers,
)
from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_mismatched_feedback_channel import (
    evaluate_partitioned_absolute_g3_feedback_column_bundle,
)
from closed_universe_observers.berger_recoil_reality_folded_shell import (
    complete_reality_folded_shell,
)
from closed_universe_observers.berger_recoil_real_shell_extraction import (
    extract_real_channel_column_sum,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_TWO_J6_REALITY_FOLDED_BINDING.json"
SCHEMA = PACKAGE / "schema/berger-recoil-two-j6-reality-folded-binding-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-two-j6-reality-folded-binding.md"
DEPENDENCIES = {
    "symbolic_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "first_omitted": PACKAGE / "certificates/BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json",
    "two_j5_binding": PACKAGE / "certificates/BERGER_RECOIL_TWO_J5_ALL_CHANNEL_COLUMN_BINDING.json",
    "direct_gate": PACKAGE / "certificates/BERGER_RECOIL_DIRECT_SHELL_AND_TAIL_STOP_GATE.json",
    "reality": PACKAGE / "certificates/BERGER_RECOIL_REAL_SHELL_EXTRACTION.json",
    "matched_backend": PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK.json",
    "mismatched_backend": PACKAGE / "certificates/BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "cross_remainder": PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "exact_kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_reality_folded_shell.py",
    PACKAGE / "berger_recoil_real_shell_extraction.py",
    PACKAGE / "berger_recoil_direct_finite_shell_provider.py",
    PACKAGE / "berger_recoil_first_omitted_shell_binding.py",
    PACKAGE / "berger_recoil_mismatched_feedback_channel.py",
    PACKAGE / "verify_berger_recoil_two_j6_reality_folded_binding.py",
    PACKAGE / "tests/test_berger_recoil_two_j6_reality_folded_binding.py",
    SCHEMA,
    REPORT,
]
TWO_J = 6
REPRESENTATIVE_COLUMNS = tuple(range(TWO_J // 2 + 1))
VALIDATION_MASS_SQUARED = RationalInterval(Fraction(1), Fraction(2))
PARTITION_COUNT = 2
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
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    carriers5 = bind_first_omitted_shell_direct_carriers(
        detector_image_certificate=values["detector_image"],
        cross_window_remainder_certificate=values["cross_remainder"],
        exact_kernel_certificate=values["exact_kernels"],
        first_omitted_shell_certificate=values["first_omitted"],
    )
    shell6 = build_direct_finite_shell_payload(
        two_j=TWO_J,
        detector_base_certificate=values["detector_image"],
        cross_window_base_certificate=values["cross_remainder"],
        kernel_base_certificate=values["exact_kernels"],
        moment_certificate=values["moments"],
        detector_profile_certificate=values["profiles"],
        switch_certificate=values["switches"],
        spectral_certificate=values["spectral"],
    )
    expected_hash = values["direct_gate"]["direct_shell_provider"]["sentinel_payload_sha256"]
    if shell6["payload_sha256"] != expected_hash:
        raise ValueError("two_j=6 direct-shell sentinel payload drifted")
    carriers6 = bind_direct_finite_shell_payload(
        detector_image_certificate=carriers5["detector_image"],
        cross_window_remainder_certificate=carriers5["cross_window_remainder"],
        exact_kernel_certificate=carriers5["exact_kernel"],
        shell_payload=shell6,
    )
    return {**values, **carriers6, "shell6": shell6}


def _compute_column(column: int) -> dict[str, Any]:
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
        mass_squared_intervals={0: VALIDATION_MASS_SQUARED, 1: VALIDATION_MASS_SQUARED},
        partition_count=PARTITION_COUNT,
        radical_bits=RADICAL_BITS,
        outward_bits=OUTWARD_BITS,
    )
    return {
        "two_j": TWO_J,
        "column": column,
        "partition_count": PARTITION_COUNT,
        "channels": [_summary(row) for row in rows],
    }


def _compute_representatives() -> list[dict[str, Any]]:
    _worker_context()  # Prewarm before fork so the 64-second shell build is shared.
    with ProcessPoolExecutor(max_workers=WORKER_COUNT) as executor:
        rows = list(executor.map(_compute_column, REPRESENTATIVE_COLUMNS))
    return sorted(rows, key=lambda row: row["column"])


def _partner_mutation_detected(rows: list[dict[str, Any]]) -> bool:
    mutated = json.loads(json.dumps(rows))
    partner = next(row for row in mutated if row["column"] == TWO_J)
    channel = next(row for row in partner["channels"] if row["channel_id"] == "I_000")
    channel["coefficient_block_interval"]["real"]["upper"] = str(
        Fraction(channel["coefficient_block_interval"]["real"]["upper"]) + 1
    )
    grouped = [
        row
        for bundle in mutated
        for row in bundle["channels"]
        if row["channel_id"] == "I_000"
    ]
    try:
        extract_real_channel_column_sum(grouped)
    except ValueError as error:
        return "conjugate carrier rectangles" in str(error)
    return False


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "symbolic_word": "ALL_EIGHT_ABC_RECOIL_CHANNEL_WORDS_EXPORTED",
        "first_omitted": "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED",
        "two_j5_binding": "ALL_48_TWO_J5_CHANNEL_COLUMN_BLOCKS_EVALUATED",
        "direct_gate": "DIRECT_FINITE_SHELL_SENTINEL_TWO_J6_EXPORTED",
        "reality": "COMPLEX_CHANNEL_TO_REAL_SHELL_SCALAR_MAP_CERTIFIED",
        "matched_backend": "ALL_MATCHED_FEEDBACK_SWITCH_OCCURRENCES_CELL_PARTITIONED",
        "mismatched_backend": "ALL_EIGHT_ABC_TWO_J0_K0_INTERVALS_EVALUATED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    representatives = _compute_representatives()
    folded = complete_reality_folded_shell(
        two_j=TWO_J, representative_columns=representatives
    )
    completed = folded["completed_columns"]
    rows = [row for bundle in completed for row in bundle["channels"]]
    coverage = {(row["channel_id"], row["column"]) for row in rows}
    expected = {(channel, column) for channel in CHANNELS for column in range(TWO_J + 1)}
    if coverage != expected or len(rows) != 56:
        raise AssertionError("two_j=6 channel-column coverage is incomplete")
    causal_zeros = [row for row in rows if row["causal_support_zero"]]
    if len(causal_zeros) != 28 or {row["channel_id"] for row in causal_zeros} != CAUSAL_ZERO_CHANNELS:
        raise AssertionError("two_j=6 causal-zero classification drifted")
    if folded["direct_channel_column_count"] != 32 or folded["reality_derived_channel_column_count"] != 24:
        raise AssertionError("two_j=6 direct/derived split drifted")
    allowed = [row for row in rows if not row["causal_support_zero"]]
    all_allowed_contain_zero = all(row["coefficient_block_contains_zero"] for row in allowed)
    if not all_allowed_contain_zero:
        raise AssertionError("a two_j=6 allowed channel unexpectedly excludes zero")
    if any(
        row["imaginary_column_sum"] != {"lower": "0", "upper": "0", "width": "0"}
        for row in folded["real_channel_sums"]
    ):
        raise AssertionError("two_j=6 shell retained an imaginary component")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL finite-shell result "
        "binds the complete direct two_j=6 absolute-g3 feedback shell. The "
        "cell-partitioned causal backend directly evaluates all eight I_abc "
        "channels at the four SU(2) reality representatives k=0,1,2,3, for 32 "
        "direct channel-column blocks. The certified conjugate-column theorem "
        "derives the remaining 24 blocks at k=6,5,4 without treating independent "
        "interval rectangles as correlated by assumption. Thus all 56 blocks "
        "are certified: 28 support-forbidden blocks are exact zeros and all 28 "
        "causally allowed enclosures contain zero on the validation mass-squared "
        "domain [1,2]. The central k=3 rectangles are self-conjugate, and all "
        "eight passive-column sums are exported as real intervals. This completes "
        "the declared two_j=6 feedback gate but does not choose physical masses, "
        "couplings or a stopping goal, run the unbounded shell stream, prove a "
        "nonzero recoil correction or determinant, descend the apparatus quotient, "
        "restrict to the second-order cone, activate Bridge 3 or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-two-j6-reality-folded-binding-v1",
        "result_id": "BERGER_RECOIL_TWO_J6_REALITY_FOLDED_BINDING",
        "setting_id": values["symbolic_word"]["setting_id"],
        "claim_status": "ALL_56_TWO_J6_CHANNEL_COLUMNS_CERTIFIED_BY_32_DIRECT_AND_24_REALITY_DERIVED_BLOCKS",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "strictly ordered h0,D0,h1,D1 compact windows; no spatial boundary",
            "charge_sector": "fixed-coupling Berger validation sector",
            "carrier": "direct two_j=6 detector-polynomial/kernel carrier with explicit SU(2) conjugate-column completion",
            "degree": "Maxwell one/two-form and physical massive two-form blocks",
            "parity": "all D_a/source_b/feedback_c labels with D0 axial and D1 transverse polarizations",
            "ell": "direct finite shell two_j=6",
            "m": "all seven representation rows",
            "k": "direct representatives k=0,1,2,3 and exact reality partners k=6,5,4",
            "omega": "partition-two enclosures on both mass-squared intervals [1,2]",
        },
        "evaluation_contract": {
            "partition_count": PARTITION_COUNT,
            "outward_rounding_bits": OUTWARD_BITS,
            "radical_bits": RADICAL_BITS,
            "validation_mass_squared_intervals": {"0": VALIDATION_MASS_SQUARED.serialize(), "1": VALIDATION_MASS_SQUARED.serialize()},
            "representative_columns": list(REPRESENTATIVE_COLUMNS),
            "direct_shell_payload_sha256": _worker_context()["shell6"]["payload_sha256"],
            "hashed_exact_T_two_j138_stream_identification_status": "NO_CERTIFIED_MAP",
        },
        "completed_columns": completed,
        "two_j6_real_channel_sums": folded["real_channel_sums"],
        "coverage_summary": {
            "total_channel_column_count": len(rows),
            "direct_backend_count": folded["direct_channel_column_count"],
            "exact_reality_derived_count": folded["reality_derived_channel_column_count"],
            "causal_support_zero_count": len(causal_zeros),
            "causally_allowed_count": len(allowed),
            "all_causally_allowed_rectangles_contain_zero": all_allowed_contain_zero,
        },
        "mutation_results": [
            {"name": "evaluate_both_members_of_each_reality_pair_independently", "detected": folded["reality_derived_channel_column_count"] == 24, "witness": "only k=0,1,2,3 enter the direct backend"},
            {"name": "alter_one_derived_partner_rectangle", "detected": _partner_mutation_detected(completed)},
            {"name": "identify_hashed_exact_T_stream_by_mode_label", "detected": values["direct_gate"]["direct_shell_provider"]["hashed_exact_T_two_j138_stream_identification_status"] == "NO_CERTIFIED_MAP"},
        ],
        "flags": {
            "TWO_J6_REPRESENTATIVE_COLUMNS_DIRECTLY_EVALUATED": True,
            "TWO_J6_REALITY_PARTNER_COLUMNS_EXACTLY_DERIVED": True,
            "ALL_56_TWO_J6_CHANNEL_COLUMN_BLOCKS_CERTIFIED": True,
            "ALL_EIGHT_TWO_J6_REAL_CHANNEL_SUMS_EXPORTED": True,
            "TWO_J6_FEEDBACK_CHANNELS_EVALUATED": True,
            "PHYSICAL_MASS_COUPLING_SPECIALIZATION_EXPORTED": False,
            "FOUR_PHYSICAL_RECOIL_INTERVALS_EXPORTED": False,
            "RECOIL_CORRECTED_RESPONSE_RANK_TWO_CERTIFIED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "AUDIT_AND_EXPORT_THE_GENERIC_REALITY_FOLDED_SHELL_STREAM_ADAPTER_BEFORE_REQUESTING_PHYSICAL_PARAMETERS",
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
    if args.check and (not CERTIFICATE.exists() or CERTIFICATE.read_text() != rendered):
        raise SystemExit("stale Berger two_j=6 reality-folded binding certificate")
    print("BERGER_RECOIL_TWO_J6_REALITY_FOLDED_BINDING generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
