#!/usr/bin/env python3
"""Evaluate the six mismatched Berger absolute-g3 feedback channels."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_mismatched_feedback_channel import (
    evaluate_partitioned_absolute_g3_feedback_channel,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS.json"
SCHEMA = PACKAGE / "schema/berger-six-mismatched-absolute-g3-feedback-channels-v1.schema.json"
REPORT = PACKAGE / "reports/berger-six-mismatched-absolute-g3-feedback-channels.md"
DEPENDENCIES = {
    "symbolic_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "matched_feedback": PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK.json",
    "cross_remainder": PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "exact_kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_mismatched_feedback_channel.py",
    PACKAGE / "verify_berger_six_mismatched_feedback_channels.py",
    PACKAGE / "tests/test_berger_six_mismatched_feedback_channels.py",
    SCHEMA,
    REPORT,
]
VALIDATION_MASS_SQUARED = RationalInterval(Fraction(1), Fraction(2))
PARTITION_RAIL = (2, 4, 8)
MISMATCHED = ((0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0))
CAUSALLY_ALLOWED = ((1, 0, 0), (1, 0, 1))


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


def _summary(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "channel_id": value["channel_id"],
        "detector": value["detector"],
        "source_preparation": value["source_preparation"],
        "feedback_emitter": value["feedback_emitter"],
        "partition_count": value["partition_count"],
        "coefficient_block_interval": value["coefficient_block_interval"],
        "coefficient_block_contains_zero": _contains_zero(
            value["coefficient_block_interval"]
        ),
        "causal_support_zero": value["causal_support_zero"],
        "causal_zero_reason": value["causal_zero_reason"],
        "absolute_g3_monomial": value["absolute_g3_monomial"],
        "cross_window_detector_remainder_applied": value.get(
            "cross_window_detector_remainder_applied", False
        ),
        "cross_window_retarded_propagation": value.get(
            "cross_window_retarded_propagation", False
        ),
        "full_payload_sha256": _payload_hash(value),
    }


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    required = {
        "symbolic_word": "ALL_EIGHT_ABC_RECOIL_CHANNEL_WORDS_EXPORTED",
        "matched_feedback": "MATCHED_FEEDBACK_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8",
        "cross_remainder": "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED",
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "SWITCHES_C_INFINITY_COMPACT_SUPPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "exact_kernels": "MASSIVE_ONE_FORM_CORRECTION_BLOCKS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    common = {
        "detector_image_certificate": values["detector_image"],
        "cross_window_remainder_certificate": values["cross_remainder"],
        "detector_profile_certificate": values["profiles"],
        "switch_certificate": values["switches"],
        "moment_certificate": values["moments"],
        "exact_kernel_certificate": values["exact_kernels"],
        "two_j": 0,
        "column": 0,
        "source_mass_squared_interval": VALIDATION_MASS_SQUARED,
        "feedback_mass_squared_interval": VALIDATION_MASS_SQUARED,
    }
    causal_zero_rows = []
    allowed_rails: dict[str, list[dict[str, Any]]] = {}
    for channel in MISMATCHED:
        if channel in CAUSALLY_ALLOWED:
            rows = [
                _summary(
                    evaluate_partitioned_absolute_g3_feedback_channel(
                        detector=channel[0],
                        source_preparation=channel[1],
                        feedback_emitter=channel[2],
                        partition_count=count,
                        **common,
                    )
                )
                for count in PARTITION_RAIL
            ]
            allowed_rails[rows[0]["channel_id"]] = rows
        else:
            causal_zero_rows.append(
                _summary(
                    evaluate_partitioned_absolute_g3_feedback_channel(
                        detector=channel[0],
                        source_preparation=channel[1],
                        feedback_emitter=channel[2],
                        partition_count=8,
                        **common,
                    )
                )
            )
    if len(causal_zero_rows) != 4 or not all(
        row["causal_support_zero"] for row in causal_zero_rows
    ):
        raise AssertionError("four mismatched support zeros were not certified")
    if {row["causal_zero_reason"] for row in causal_zero_rows} != {
        "FEEDBACK_WINDOW_STRICTLY_BEFORE_SOURCE_WINDOW",
        "DETECTOR_WINDOW_STRICTLY_BEFORE_FEEDBACK_WINDOW",
    }:
        raise AssertionError("causal-zero reason ledger is incomplete")
    for channel_id, rows in allowed_rails.items():
        if any(row["causal_support_zero"] for row in rows):
            raise AssertionError(f"{channel_id} was incorrectly zeroed by support")
        if not all(row["coefficient_block_contains_zero"] for row in rows):
            raise AssertionError(f"{channel_id} unexpectedly excludes zero")
        for component in ("real", "imaginary"):
            widths = [
                Fraction(row["coefficient_block_interval"][component]["width"])
                for row in rows
            ]
            if not widths[0] > widths[1] > widths[2]:
                raise AssertionError(f"{channel_id} {component} widths did not contract")
    if not allowed_rails["I_100"][-1]["cross_window_detector_remainder_applied"]:
        raise AssertionError("I_100 omitted the D1/h0 cross-window remainder")
    if not allowed_rails["I_101"][-1]["cross_window_retarded_propagation"]:
        raise AssertionError("I_101 omitted h0-to-h1 retarded propagation")

    mutated = deepcopy(values["cross_remainder"])
    mutated["flags"]["D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED"] = False
    cross_remainder_mutation_detected = False
    try:
        evaluate_partitioned_absolute_g3_feedback_channel(
            detector=1,
            source_preparation=0,
            feedback_emitter=0,
            partition_count=2,
            **{**common, "cross_window_remainder_certificate": mutated},
        )
    except ValueError:
        cross_remainder_mutation_detected = True
    if not cross_remainder_mutation_detected:
        raise AssertionError("missing cross-window remainder was not detected")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL finite-channel result "
        "evaluates all six mismatched two_j=0,k=0 absolute-g3 coefficient "
        "blocks on the validation mass-squared domain [1,2]. Strict support "
        "ordering h0<D0<h1<D1 makes I_001, I_010, I_011 and I_110 exactly "
        "zero. I_100 uses the certified D1 advanced-detector remainder on h0; "
        "I_101 propagates the h0 source retardedly to h1. Both causally allowed "
        "complex enclosures contract strictly on the 2/4/8-cell rail but still "
        "contain zero. Together with the matched-channel dependency, all eight "
        "I_abc blocks are now evaluated at this one finite mode/column and "
        "validation mass domain. No nonzero, sign, recoil-rank, physical-mass, "
        "higher-shell, tail, quotient, tangent-cone, Bridge-3 or quantum claim "
        "follows."
    )
    return {
        "schema": "closed-universe-berger-six-mismatched-absolute-g3-feedback-channels-v1",
        "result_id": "BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS",
        "setting_id": values["symbolic_word"]["setting_id"],
        "claim_status": "SIX_MISMATCHED_CHANNELS_EVALUATED_FOUR_CAUSAL_ZEROS_TWO_ZERO_CONTAINING",
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
            "carrier": "six cell-partitioned mismatched advanced/retarded Maxwell-massive coefficient blocks",
            "degree": "Maxwell one-form, field-strength two-form and physical massive two-form",
            "parity": "all mismatched D_a/source_b/feedback_c labels",
            "ell": "two_j=0",
            "m": "all component-major form rows",
            "k": "passive column k=0",
            "omega": "2/4/8-cell causal enclosures on source and feedback mass squared in [1,2]",
        },
        "causal_support_zero_channels": causal_zero_rows,
        "causally_allowed_partition_rails": allowed_rails,
        "mutation_results": [
            {
                "name": "drop_D1_to_h0_cross_window_remainder",
                "detected": cross_remainder_mutation_detected,
            },
            {
                "name": "promote_zero_containing_allowed_channels_to_nonzero",
                "detected": all(
                    rows[-1]["coefficient_block_contains_zero"]
                    for rows in allowed_rails.values()
                ),
            },
        ],
        "flags": {
            "SIX_MISMATCHED_TWO_J0_K0_CHANNELS_EVALUATED": True,
            "FOUR_MISMATCHED_CHANNELS_CERTIFIED_CAUSAL_ZERO": True,
            "TWO_CAUSALLY_ALLOWED_MISMATCHED_CHANNELS_INTERVAL_EVALUATED": True,
            "ALLOWED_MISMATCHED_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8": True,
            "ALLOWED_MISMATCHED_PARTITION8_INTERVALS_EXCLUDE_ZERO": False,
            "ALL_EIGHT_ABC_TWO_J0_K0_INTERVALS_EVALUATED": True,
            "ALL_EIGHT_ABC_ALL_SHELL_INTERVALS_EVALUATED": False,
            "PHYSICAL_MASS_SPECIALIZATION_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EXTEND_THE_DETECTOR_AND_FEEDBACK_PROVIDER_BEYOND_TWO_J4",
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
        raise SystemExit("certificate drift")
    print("BERGER_SIX_MISMATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
