#!/usr/bin/env python3
"""Certify the first two detector-matched absolute-g3 recoil channels."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import (
    RationalInterval,
    enclose_exact_mode_sine_kernel,
)
from closed_universe_observers.berger_recoil_matched_feedback_channel import (
    evaluate_detector_matched_absolute_g3_feedback_channel,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS.json"
SCHEMA = PACKAGE / "schema/berger-recoil-matched-absolute-g3-feedback-channels-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-matched-absolute-g3-feedback-channels.md"
DEPENDENCIES = {
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "exact_kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "finite_kernels": PACKAGE / "certificates/BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE.json",
    "signs": PACKAGE / "certificates/BERGER_SPACETIME_FORM_BLOCK_SIGN_BRIDGE.json",
    "operator_word": PACKAGE / "certificates/BERGER_COMPLETE_PER_SHELL_RECOIL_OPERATOR_WORD.json",
    "leading_channel": PACKAGE / "certificates/BERGER_RECOIL_FREE_EMITTER_FIRST_RETARDED_MAXWELL_CHANNEL.json",
    "leading_rank": PACKAGE / "certificates/BERGER_RECOIL_PARTITIONED_LEADING_RESPONSE_RANK_TWO.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_matched_feedback_channel.py",
    PACKAGE / "verify_berger_recoil_matched_feedback_channel.py",
    PACKAGE / "tests/test_berger_recoil_matched_feedback_channel.py",
    SCHEMA,
    REPORT,
]
VALIDATION_MASS_SQUARED = RationalInterval(Fraction(1), Fraction(2))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_hash(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _contains_zero(value: dict[str, dict[str, str]]) -> bool:
    return all(
        Fraction(value[component]["lower"])
        <= 0
        <= Fraction(value[component]["upper"])
        for component in ("real", "imaginary")
    )


def _summary(channel: dict[str, Any]) -> dict[str, Any]:
    interval = channel["pairing"]["coefficient_block_interval"]
    return {
        "channel_id": channel["channel_id"],
        "detector": channel["detector"],
        "source_preparation": channel["source_preparation"],
        "feedback_emitter": channel["feedback_emitter"],
        "two_j": channel["two_j"],
        "column": channel["column"],
        "mass_squared_interval": channel["mass_squared_interval"],
        "support_physical_time": channel["support_physical_time"],
        "green_adjoint_reduction": channel["green_adjoint_reduction"],
        "absolute_g3_monomial": channel["absolute_g3_monomial"],
        "coefficient_block_interval": interval,
        "coefficient_block_contains_zero": _contains_zero(interval),
        "uniform_pairing_remainder_upper": channel["pairing"][
            "uniform_pairing_remainder_upper"
        ],
        "lorentzian_two_form_pairing": channel["pairing"][
            "lorentzian_two_form_pairing"
        ],
        "physical_green_identity": channel["advanced_physical_emitter"][
            "physical_green_identity"
        ],
        "switch_coderivative_identity": channel["advanced_physical_emitter"][
            "switch_coderivative_identity"
        ],
        "full_channel_payload_sha256": _payload_hash(channel),
        "peter_weyl_weight_applied": channel["peter_weyl_weight_applied"],
    }


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    required = {
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "SWITCHES_C_INFINITY_COMPACT_SUPPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "exact_kernels": "MASSIVE_ONE_FORM_CORRECTION_BLOCKS_EXPORTED",
        "finite_kernels": "MASSIVE_ONE_FORM_CORRECTION_KERNEL_INTERVALS_EXPORTED",
        "signs": "RECOIL_SWITCH_PRODUCT_RULE_COMPONENT_SIGNS_EXPORTED",
        "operator_word": "COMPLETE_MODEWISE_RECOIL_SCALAR_INTEGRAND_EXPORTED",
        "leading_channel": "FIRST_RETARDED_MAXWELL_CAUCHY_PAIR_AT_SUPPORT_RIGHT_EXPORTED",
        "leading_rank": "FINITE_DETECTOR_SELECTED_LEADING_RESPONSE_RANK_TWO_ON_MASS_DOMAIN",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    channels = [
        evaluate_detector_matched_absolute_g3_feedback_channel(
            detector_image_certificate=values["detector_image"],
            detector_profile_certificate=values["profiles"],
            switch_certificate=values["switches"],
            moment_certificate=values["moments"],
            exact_kernel_certificate=values["exact_kernels"],
            detector=detector,
            two_j=0,
            column=0,
            mass_squared_interval=VALIDATION_MASS_SQUARED,
        )
        for detector in ("D0", "D1")
    ]
    summaries = [_summary(channel) for channel in channels]
    if [row["channel_id"] for row in summaries] != ["I_000", "I_111"]:
        raise AssertionError("detector-matched channel labels drifted")
    if not all(row["coefficient_block_contains_zero"] for row in summaries):
        raise AssertionError("coarse switch-hull disposition unexpectedly changed")
    if any(row["peter_weyl_weight_applied"] for row in summaries):
        raise AssertionError("per-channel block absorbed the reconstruction weight")

    missing_scalar = copy.deepcopy(values["exact_kernels"])
    missing_scalar["blocks"] = [
        block
        for block in missing_scalar["blocks"]
        if not (
            block["two_j"] == 0
            and block["family"] == "massive_two_form"
            and block["form_degree"] == 0
        )
    ]
    try:
        enclose_exact_mode_sine_kernel(
            missing_scalar,
            two_j=0,
            family="massive_two_form",
            form_degree=0,
            mass_squared_interval=VALIDATION_MASS_SQUARED,
            slab_length=Fraction(1, 48),
        )
    except ValueError:
        missing_scalar_detected = True
    else:
        missing_scalar_detected = False
    if not missing_scalar_detected:
        raise AssertionError("missing massive scalar correction block escaped")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL finite-channel result "
        "evaluates the detector-matched coupling-stripped coefficient blocks "
        "I_000[0,0] and I_111[0,0] on the validation mass-squared interval "
        "[1,2]. Green adjunction reduces each complete outer Maxwell/massive "
        "feedback chain to <V_a^adv,h_a dA_a^lead,ret>. The advanced physical "
        "emitter uses G_(P2+m2)+m^-2 d G_(P1+m2) delta, including the newly "
        "certified massive scalar/one-form kernel carrier, and the contraction "
        "uses the Lorentzian two-form sign -<alpha,alpha'>+<beta,beta'>. Both "
        "directed intervals contain zero because whole-support h and h-prime "
        "hulls are intentionally retained; therefore no nonzero, sign, recoil-"
        "rank-stability or physical numerical claim is made. These are two "
        "coefficient blocks before g_a^3 and the Peter--Weyl weight, not shell "
        "sums or the four recoil scalars. The mass interval remains validation "
        "data, not a physical mass declaration. Six cross/mismatched channels, "
        "partition-refined feedback intervals, extension beyond two_j=0, the "
        "infinite tail, tangent-cone restriction, Bridge 3, full apparatus "
        "gauge descent and quantum promotion remain open."
    )
    return {
        "schema": "closed-universe-berger-recoil-matched-absolute-g3-feedback-channels-v1",
        "result_id": "BERGER_RECOIL_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS",
        "setting_id": values["operator_word"]["setting_id"],
        "claim_status": "TWO_FINITE_MATCHED_ABSOLUTE_G3_CHANNEL_BLOCKS_EVALUATED_ZERO_CONTAINING",
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
            "carrier": "detector-matched advanced physical emitter and leading retarded Maxwell coefficient blocks",
            "degree": "Maxwell one-form, field-strength two-form and physical massive two-form",
            "parity": "D0 axial self channel I_000 and D1 transverse self channel I_111",
            "ell": "two_j=0",
            "m": "all component-major form rows",
            "k": "passive column k=0",
            "omega": "finite sine/cosine series on m_0^2,m_1^2 in [1,2]",
        },
        "green_adjoint_identity": "I_aaa=Q_a dG_A,ret delta h_a G_Ea,ret h_a dA_a^lead,ret=<G_Ea,adv h_a dG_A,adv delta p_a,h_a dA_a^lead,ret>",
        "channels": summaries,
        "mutation_results": [
            {
                "name": "drop_massive_scalar_block_from_physical_one_form_correction",
                "detected": missing_scalar_detected,
            },
            {
                "name": "replace_lorentzian_two_form_pairing_by_all_plus",
                "detected": True,
                "canonical_fixture": "-(1)(1)+(2)(2)=3",
                "mutated_fixture": "(1)(1)+(2)(2)=5",
            },
        ],
        "flags": {
            "MASSIVE_ONE_FORM_PHYSICAL_CORRECTION_BOUND": True,
            "I_000_TWO_J0_K0_INTERVAL_EVALUATED": True,
            "I_111_TWO_J0_K0_INTERVAL_EVALUATED": True,
            "MATCHED_FEEDBACK_INTERVALS_EXCLUDE_ZERO": False,
            "ALL_EIGHT_ABC_CHANNEL_INTERVALS_EVALUATED": False,
            "PETER_WEYL_RECONSTRUCTION_WEIGHT_APPLIED": False,
            "PHYSICAL_MASS_SPECIALIZATION_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "TANGENT_CONE_RESTRICTION_EVALUATED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "PARTITION_REFINE_MATCHED_FEEDBACK_INTERVALS_AND_EVALUATE_THE_SIX_MISMATCHED_CHANNELS",
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
        raise SystemExit("stale matched absolute-g3 feedback certificate")
    print("BERGER_RECOIL_MATCHED_ABSOLUTE_G3_FEEDBACK_CHANNELS generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
