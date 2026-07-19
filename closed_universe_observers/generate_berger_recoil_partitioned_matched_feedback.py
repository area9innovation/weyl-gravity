#!/usr/bin/env python3
"""Certify cell-partition refinement of the two matched feedback channels."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
)
from closed_universe_observers.berger_recoil_partitioned_feedback_channel import (
    evaluate_partitioned_detector_matched_absolute_g3_feedback_channel,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK.json"
SCHEMA = PACKAGE / "schema/berger-recoil-partitioned-matched-absolute-g3-feedback-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-partitioned-matched-absolute-g3-feedback.md"
DEPENDENCIES = {
    "coarse_feedback": PACKAGE / "certificates/BERGER_RECOIL_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS.json",
    "leading_partition": PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO.json",
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "exact_kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_partitioned_feedback_channel.py",
    PACKAGE / "verify_berger_recoil_partitioned_matched_feedback.py",
    PACKAGE / "tests/test_berger_recoil_partitioned_matched_feedback.py",
    SCHEMA,
    REPORT,
]
VALIDATION_MASS_SQUARED = RationalInterval(Fraction(1), Fraction(2))
PARTITION_RAIL = (2, 4, 8)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _contains_zero(interval: dict[str, dict[str, str]]) -> bool:
    return all(
        Fraction(interval[component]["lower"])
        <= 0
        <= Fraction(interval[component]["upper"])
        for component in ("real", "imaginary")
    )


def _summary(channel: dict[str, Any]) -> dict[str, Any]:
    interval = channel["coefficient_block_interval"]
    return {
        "channel_id": channel["channel_id"],
        "detector": channel["detector"],
        "partition_count": channel["partition_count"],
        "cell_width": channel["cell_width"],
        "mass_squared_interval": channel["mass_squared_interval"],
        "coefficient_block_interval": interval,
        "coefficient_block_contains_zero": _contains_zero(interval),
        "full_cellwise_payload_sha256": _payload_hash(channel),
    }


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    required = {
        "coarse_feedback": "I_000_TWO_J0_K0_INTERVAL_EVALUATED",
        "leading_partition": "CELL_PARTITIONED_POSITIVE_SWITCH_GREEN_INTEGRATION_EXPORTED",
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "SWITCHES_C_INFINITY_COMPACT_SUPPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "exact_kernels": "MASSIVE_ONE_FORM_CORRECTION_BLOCKS_EXPORTED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    rails = {
        detector: [
            _summary(
                evaluate_partitioned_detector_matched_absolute_g3_feedback_channel(
                    detector_image_certificate=values["detector_image"],
                    detector_profile_certificate=values["profiles"],
                    switch_certificate=values["switches"],
                    moment_certificate=values["moments"],
                    exact_kernel_certificate=values["exact_kernels"],
                    detector=detector,
                    two_j=0,
                    column=0,
                    mass_squared_interval=VALIDATION_MASS_SQUARED,
                    partition_count=count,
                )
            )
            for count in PARTITION_RAIL
        ]
        for detector in ("D0", "D1")
    }
    for detector, rows in rails.items():
        for earlier, later in zip(rows, rows[1:]):
            for component in ("real", "imaginary"):
                earlier_width = Fraction(
                    earlier["coefficient_block_interval"][component]["width"]
                )
                later_width = Fraction(
                    later["coefficient_block_interval"][component]["width"]
                )
                if not later_width < earlier_width:
                    raise AssertionError(
                        f"{detector} {component} interval failed to contract"
                    )
    if not all(row["coefficient_block_contains_zero"] for rows in rails.values() for row in rows):
        raise AssertionError("partition rail unexpectedly excluded zero")

    coarse = {
        row["detector"]: row
        for row in values["coarse_feedback"]["channels"]
    }
    refinements = {}
    for detector, rows in rails.items():
        refined = rows[-1]
        coarse_interval = coarse[detector]["coefficient_block_interval"]
        refinements[detector] = {
            "channel_id": refined["channel_id"],
            "coarse_real_width": coarse_interval["real"]["width"],
            "partition8_real_width": refined["coefficient_block_interval"]["real"]["width"],
            "coarse_imaginary_width": coarse_interval["imaginary"]["width"],
            "partition8_imaginary_width": refined["coefficient_block_interval"]["imaginary"]["width"],
            "real_width_strictly_reduced": Fraction(
                refined["coefficient_block_interval"]["real"]["width"]
            ) < Fraction(coarse_interval["real"]["width"]),
            "imaginary_width_strictly_reduced": Fraction(
                refined["coefficient_block_interval"]["imaginary"]["width"]
            ) < Fraction(coarse_interval["imaginary"]["width"]),
            "zero_still_contained": refined["coefficient_block_contains_zero"],
        }
    if not all(
        row["real_width_strictly_reduced"]
        and row["imaginary_width_strictly_reduced"]
        for row in refinements.values()
    ):
        raise AssertionError("partition-8 rail did not improve the coarse enclosure")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL finite-channel result "
        "replaces every whole-support h/h-prime hull in the matched I_000[0,0] "
        "and I_111[0,0] pipelines by common 2-, 4- and 8-cell partitions. The "
        "advanced physical massive field, partition-selected leading emitter "
        "preparation, retarded Maxwell field strength and final Lorentzian "
        "pairing are all propagated cellwise. Full causal source cells use exact "
        "cell lengths; each diagonal Volterra triangle is rigorously "
        "over-enclosed by a length in [0,cell_width], so its dependency loss "
        "contracts under refinement. Real and imaginary widths strictly decrease "
        "at every rail step for both channels and are strictly smaller than the "
        "coarse certificate. Both partition-8 intervals still contain zero, so "
        "no sign, nonvanishing or recoil-corrected rank claim follows. The mass "
        "interval [1,2] is validation data, not a physical mass declaration. Six "
        "mismatched channels, further time/mass refinement, higher shells, tail "
        "aggregation, tangent-cone restriction, Bridge 3, full apparatus quotient "
        "and quantum promotion remain open."
    )
    return {
        "schema": "closed-universe-berger-recoil-partitioned-matched-absolute-g3-feedback-v1",
        "result_id": "BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK",
        "setting_id": values["coarse_feedback"]["setting_id"],
        "claim_status": "MATCHED_FEEDBACK_INTERVALS_STRICTLY_NARROWED_ZERO_CONTAINMENT_PERSISTS",
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
            "boundaries": "matched h0/D0 and h1/D1 compact switch slabs; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "cell-partitioned matched advanced physical emitter and leading retarded Maxwell coefficient blocks",
            "degree": "Maxwell one-form, field-strength two-form and physical massive two-form",
            "parity": "D0 axial self channel I_000 and D1 transverse self channel I_111",
            "ell": "two_j=0",
            "m": "all component-major form rows",
            "k": "passive column k=0",
            "omega": "2/4/8-cell causal enclosures on m_0^2,m_1^2 in [1,2]",
        },
        "partition_rails": rails,
        "coarse_to_partition8_refinement": refinements,
        "mutation_results": [
            {
                "name": "collapse_partition_rail_to_whole_support_hulls",
                "detected": True,
                "evidence": "both real and imaginary partition-8 widths are strictly below the coarse widths",
            },
            {
                "name": "promote_zero_containing_intervals_to_nonzero",
                "detected": True,
                "evidence": "both partition-8 complex rectangles still contain zero",
            },
        ],
        "flags": {
            "ALL_MATCHED_FEEDBACK_SWITCH_OCCURRENCES_CELL_PARTITIONED": True,
            "MATCHED_FEEDBACK_WIDTHS_STRICTLY_CONTRACT_2_TO_4_TO_8": True,
            "PARTITION8_WIDTHS_STRICTLY_BELOW_COARSE_HULLS": True,
            "PARTITION8_MATCHED_FEEDBACK_INTERVALS_EXCLUDE_ZERO": False,
            "ALL_EIGHT_ABC_CHANNEL_INTERVALS_EVALUATED": False,
            "PHYSICAL_MASS_SPECIALIZATION_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "EVALUATE_SIX_MISMATCHED_CHANNELS_WITH_THE_PARTITIONED_CAUSAL_BACKEND",
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
        raise SystemExit("stale partitioned matched feedback certificate")
    print("BERGER_RECOIL_PARTITIONED_MATCHED_ABSOLUTE_G3_FEEDBACK generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
