#!/usr/bin/env python3
"""Certify the switched finite diagonal massive advanced preparation stage."""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from jsonschema import Draft202012Validator

from closed_universe_observers.berger_recoil_interval_stream import RationalInterval
from closed_universe_observers.berger_recoil_massive_diagonal_preparation import (
    evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_MASSIVE_DIAGONAL_PREPARATION.json"
SCHEMA = PACKAGE / "schema/berger-recoil-massive-diagonal-preparation-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-massive-diagonal-preparation.md"
DEPENDENCIES = {
    "detector_image": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "detector_form": PACKAGE / "certificates/BERGER_RECOIL_DETECTOR_FORM_BINDING.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "switch_provider": PACKAGE / "certificates/BERGER_RECOIL_SWITCH_INTERVAL_PROVIDER.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "kernels": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "kernel_intervals": PACKAGE / "certificates/BERGER_RECOIL_FINITE_MODE_KERNEL_INTERVAL_ENCLOSURE.json",
    "matrix_engine": PACKAGE / "certificates/BERGER_RECOIL_MATRIX_INTERVAL_CONVOLUTION.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "berger_recoil_massive_diagonal_preparation.py",
    PACKAGE / "verify_berger_recoil_massive_diagonal_preparation.py",
    PACKAGE / "tests/test_berger_recoil_massive_diagonal_preparation.py",
    SCHEMA,
    REPORT,
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payload_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def build() -> dict[str, object]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    required = {
        "detector_image": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "detector_form": "EXACT_SPACETIME_DHAT1_APPLIED_TO_DETECTOR_IMAGE",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "switch_provider": "NORMALIZED_SWITCH_AND_TIME_DERIVATIVE_INTERVAL_PROVIDER_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "kernels": "MAXWELL_AND_MASSIVE_BLOCKS_TWO_J0_TO_4_EXPORTED",
        "kernel_intervals": "FINITE_MODE_KERNEL_INTERVAL_ENCLOSURES_EXPORTED",
        "matrix_engine": "SINE_KERNEL_ODD_TAU_POWERS_PRESERVED",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")
    kwargs = {
        "detector_image_certificate": values["detector_image"],
        "detector_profile_certificate": values["profiles"],
        "switch_certificate": values["switches"],
        "moment_certificate": values["moments"],
        "exact_kernel_certificate": values["kernels"],
        "mass_squared_interval": RationalInterval(Fraction(1), Fraction(2)),
    }
    d0 = evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left(
        **kwargs, detector="D0", two_j=0, column=0
    )
    d1 = evaluate_switched_detector_diagonal_massive_advanced_image_at_support_left(
        **kwargs, detector="D1", two_j=4, column=4
    )
    if d0["detector_T_to_source_y_shift"] != "1/16" or d1["detector_T_to_source_y_shift"] != "1/16":
        raise AssertionError("detector/support coordinate bridge drifted")
    if d0["kernel_nonzero_tau_powers"] != [1, 3, 5, 7, 9, 11]:
        raise AssertionError("massive sine-kernel powers drifted")
    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result translates each "
        "finite D0/D1 Dhat_1 detector polynomial from T to the advanced support "
        "coordinate, multiplies it by the certified whole-support normalized "
        "switch hull, and applies the degree-two diagonal massive sine-kernel "
        "enclosure at the support-left slice for every two_j<=4 and passive "
        "column. The adapter preserves tau powers 1,3,5,7,9,11 and propagates "
        "all source/kernel remainders. A strictly positive caller-declared "
        "mass-squared interval is runtime parameterization, not a physical mass "
        "choice. The whole-support switch hull is rigorous but deliberately "
        "coarse. This is not yet the physical Proca two-form Green operator: the "
        "I+mu^-2 Dhat_1 Deltahat_2 correction, Cauchy momentum, positive-energy "
        "dual, full spatial tail, I_abc, cone, Bridge 3 and quantum claims remain open."
    )
    return {
        "schema": "closed-universe-berger-recoil-massive-diagonal-preparation-v1",
        "result_id": "BERGER_RECOIL_MASSIVE_DIAGONAL_PREPARATION",
        "setting_id": values["detector_image"]["setting_id"],
        "claim_status": "FINITE_SWITCHED_DIAGONAL_MASSIVE_ADVANCED_SUPPORT_LEFT_IMAGE_CERTIFIED_PHYSICAL_PROCA_CORRECTION_OPEN",
        "atlas_status": "CERTIFIED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"],
        "dependency_refs": {
            name: {"path": str(path.relative_to(ROOT)), "result_id": values[name]["result_id"], "sha256": _sha256(path)}
            for name, path in DEPENDENCIES.items()
        },
        "mode_scope": {
            "theory": "classical pure-Weyl gravity plus Berger clock, Maxwell detector and massive two-form emitters",
            "background": "compact positive Berger clock at fixed coupling",
            "boundaries": "one complete compact h0 or h1 support; support-left Cauchy slice; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "switched detector-selected complex interval two-form polynomials and diagonal massive advanced-wave images",
            "degree": "spacetime two-form diagonal wave block",
            "parity": "D0 axial and D1 transverse detector profiles",
            "ell": "two_j=0,...,4",
            "m": "all component-major two-form rows",
            "k": "all passive columns k=0,...,two_j",
            "omega": "advanced support coordinate with finite sine series and uniform source/kernel remainders",
        },
        "coordinate_bridge": {
            "source_coordinate": "y=t_support_right-source_time",
            "evaluation_coordinate": "x=t_support_right-evaluation_time",
            "detector_polynomial": "T=t_detector_center-source_time=(t_detector_center-t_support_right)+y",
            "D0_shift": d0["detector_T_to_source_y_shift"],
            "D1_shift": d1["detector_T_to_source_y_shift"],
        },
        "fixtures": {"D0_two_j0_column0_sha256": _payload_sha256(d0), "D1_two_j4_column4_sha256": _payload_sha256(d1)},
        "flags": {
            "DETECTOR_TO_ADVANCED_SUPPORT_COORDINATE_TRANSLATION_EXPORTED": True,
            "NORMALIZED_SWITCH_HULL_MULTIPLIED_WITH_DHAT1_SOURCE": True,
            "DIAGONAL_MASSIVE_DEGREE_TWO_ADVANCED_IMAGE_AT_SUPPORT_LEFT_EXPORTED": True,
            "SINE_KERNEL_ODD_TAU_POWERS_PRESERVED": True,
            "PHYSICAL_PROCA_TWO_FORM_GREEN_CORRECTION_EXPORTED": False,
            "EMITTER_CAUCHY_MOMENTUM_EXPORTED": False,
            "POSITIVE_ENERGY_DUAL_COEFFICIENTS_EXPORTED": False,
            "FOUR_RECOIL_SCALAR_INTERVALS_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "APPLY_PHYSICAL_I_PLUS_MASS_INVERSE_D_DELTA_CORRECTION_AND_EXPORT_CAUCHY_PAIR",
        "claim_boundary": boundary,
        "provenance": {"source_commit": "WORKTREE", "source_manifest": [{"path": str(path.relative_to(ROOT)), "sha256": _sha256(path)} for path in SOURCE_FILES]},
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
        raise SystemExit("stale massive diagonal preparation certificate")
    print("BERGER_RECOIL_MASSIVE_DIAGONAL_PREPARATION generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
