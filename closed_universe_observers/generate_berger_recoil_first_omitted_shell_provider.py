#!/usr/bin/env python3
"""Extend the direct Berger recoil input provider to the first omitted shell."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from closed_universe_observers.generate_berger_green_weighted_detector_coderivative import (
    _clock_even_moments,
    _component_moments,
    _polynomials,
    _remainder_audit,
)
from closed_universe_observers.generate_berger_local_su2_profile_coefficients import (
    radial_moment_intervals,
)
from closed_universe_observers.generate_berger_recoil_exact_mode_kernel_payload import (
    _block,
)


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "closed_universe_observers"
CERTIFICATE = PACKAGE / "certificates/BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5.json"
SCHEMA = PACKAGE / "schema/berger-recoil-first-omitted-shell-provider-two-j5-v1.schema.json"
REPORT = PACKAGE / "reports/berger-recoil-first-omitted-shell-provider-two-j5.md"
DEPENDENCIES = {
    "detector_low": PACKAGE / "certificates/BERGER_GREEN_WEIGHTED_DETECTOR_CODERIVATIVE.json",
    "cross_low": PACKAGE / "certificates/BERGER_CROSS_WINDOW_DETECTOR_ADVANCED_MAXWELL_REMAINDER.json",
    "kernel_low": PACKAGE / "certificates/BERGER_RECOIL_EXACT_MODE_KERNEL_PAYLOAD.json",
    "moments": PACKAGE / "certificates/BERGER_VALIDATED_FLAT_BUMP_MOMENT_ENCLOSURES.json",
    "profiles": PACKAGE / "certificates/BERGER_EXACT_DETECTOR_SMEARINGS_AND_ADVANCED_COVECTORS.json",
    "switches": PACKAGE / "certificates/BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES.json",
    "spectral": PACKAGE / "certificates/BERGER_PETER_WEYL_FORM_LAPLACIAN_ENGINE.json",
}
SOURCE_FILES = [
    Path(__file__),
    PACKAGE / "generate_berger_green_weighted_detector_coderivative.py",
    PACKAGE / "generate_berger_recoil_exact_mode_kernel_payload.py",
    PACKAGE / "verify_berger_recoil_first_omitted_shell_provider.py",
    PACKAGE / "tests/test_berger_recoil_first_omitted_shell_provider.py",
    SCHEMA,
    REPORT,
]
TWO_J = 5
CORRESPONDING_TAU_MAX = {"D0": Fraction(1, 8), "D1": Fraction(5, 24)}
CROSS_D1_H0_TAU_MAX = Fraction(3, 8)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fraction_interval(values: list[str]) -> tuple[Fraction, Fraction]:
    if len(values) != 2:
        raise AssertionError("support interval is not a pair")
    return Fraction(values[0]), Fraction(values[1])


def _detector_mode(
    detector: str,
    two_j: int,
    radial: dict[int, tuple[Fraction, Fraction]],
    clock: dict[int, tuple[Fraction, Fraction]],
) -> dict[str, Any]:
    moments = _component_moments(detector, two_j, radial, clock)
    spatial, temporal = _polynomials(two_j, moments)
    return {
        "detector_id": detector,
        "two_j": two_j,
        "dimension": two_j + 1,
        "spatial_one_form_advanced_polynomial": spatial,
        "temporal_scalar_advanced_polynomial": temporal,
        "corresponding_window_remainder": _remainder_audit(
            two_j, CORRESPONDING_TAU_MAX[detector]
        ),
    }


def _manifest_hash(certificate: dict[str, Any], path: Path) -> str | None:
    relative = str(path.relative_to(ROOT))
    return next(
        (
            row["sha256"]
            for row in certificate["provenance"]["source_manifest"]
            if row["path"] == relative
        ),
        None,
    )


def build() -> dict[str, Any]:
    values = {
        name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()
    }
    required = {
        "detector_low": "FINITE_MODE_ADVANCED_MAXWELL_IMAGE_TWO_J0_TO_4_EVALUATED",
        "cross_low": "D1_ADVANCED_MAXWELL_POLYNOMIAL_REMAINDER_ON_H0_EXPORTED",
        "kernel_low": "EXACT_SINE_KERNEL_SERIES_COEFFICIENTS_EXPORTED",
        "moments": "VALIDATED_STANDARD_FLAT_BUMP_MOMENTS_EXPORTED",
        "profiles": "DETECTOR_PROFILE_CLOCK_AND_ROD_NORMALIZATION_EXACT",
        "switches": "EXACT_H0_H1_SWITCH_PROFILES_SERIALIZED",
        "spectral": "GENERIC_FINITE_PETER_WEYL_DE_RHAM_BLOCK_CONSTRUCTOR",
    }
    for name, flag in required.items():
        if values[name].get("flags", {}).get(flag) is not True:
            raise AssertionError(f"dependency dropped: {name}.{flag}")

    radial = radial_moment_intervals(values["moments"])
    clock = _clock_even_moments(values["moments"])

    detector_supports = {
        row["id"]: _fraction_interval(row["physical_time_support"])
        for row in values["profiles"]["exact_detector_profiles"]["detectors"]
    }
    switch_supports = {
        row["id"]: _fraction_interval(row["support_physical_time"])
        for row in values["switches"]["causal_support_audit"]["switches"]
    }
    derived_tau_max = {
        "D0_on_h0": detector_supports["D0"][1] - switch_supports["h_0"][0],
        "D1_on_h1": detector_supports["D1"][1] - switch_supports["h_1"][0],
        "D1_on_h0": detector_supports["D1"][1] - switch_supports["h_0"][0],
    }
    expected_tau_max = {
        "D0_on_h0": CORRESPONDING_TAU_MAX["D0"],
        "D1_on_h1": CORRESPONDING_TAU_MAX["D1"],
        "D1_on_h0": CROSS_D1_H0_TAU_MAX,
    }
    if derived_tau_max != expected_tau_max:
        raise AssertionError("declared tail radii drifted from certified supports")

    detector_generator = (
        PACKAGE / "generate_berger_green_weighted_detector_coderivative.py"
    )
    cross_generator = (
        PACKAGE / "generate_berger_cross_window_detector_advanced_remainder.py"
    )
    kernel_generator = PACKAGE / "generate_berger_recoil_exact_mode_kernel_payload.py"
    detector_source_hash_matches = (
        _manifest_hash(values["detector_low"], detector_generator)
        == _sha256(detector_generator)
    )
    cross_source_hash_matches = (
        _manifest_hash(values["cross_low"], cross_generator)
        == _sha256(cross_generator)
    )
    kernel_source_hash_matches = (
        _manifest_hash(values["kernel_low"], kernel_generator)
        == _sha256(kernel_generator)
    )
    if not all(
        (
            detector_source_hash_matches,
            cross_source_hash_matches,
            kernel_source_hash_matches,
        )
    ):
        raise AssertionError("imported direct-carrier generator provenance drifted")

    detector_rows = [
        _detector_mode(detector, TWO_J, radial, clock)
        for detector in ("D0", "D1")
    ]
    cross_remainder = _remainder_audit(TWO_J, CROSS_D1_H0_TAU_MAX)
    kernel_rows = [
        _block(TWO_J, degree, family)
        for family, degrees in (
            ("Maxwell", (0, 1)),
            ("massive_two_form", (0, 1, 2)),
        )
        for degree in degrees
    ]
    if any(row["recurrence_defect_count_through_order4"] for row in kernel_rows):
        raise AssertionError("two_j=5 kernel recurrence failed")
    if cross_remainder == detector_rows[1]["corresponding_window_remainder"]:
        raise AssertionError("D1/h1 remainder was incorrectly reused on h0")

    wrong_sign = _block(TWO_J, 1, "Maxwell", wrong_sign=True)
    if wrong_sign["recurrence_defect_count_through_order4"] == 0:
        raise AssertionError("two_j=5 kernel sign mutation escaped")

    boundary = (
        "This exact LOCAL-ALGEBRAIC/LORENTZIAN-CAUSAL result extends the direct "
        "finite Berger recoil input carrier by exactly the first omitted shell "
        "two_j=5. The same certified generic profile-moment and Peter-Weyl de "
        "Rham engines are bound to the imported two_j<=4 detector, cross-window "
        "and kernel carriers by exact source-manifest hashes before generating "
        "the new shell. D0 and D1 advanced "
        "Maxwell polynomial coefficients, their corresponding-window tails, the "
        "larger D1/h0 tail, and all Maxwell degree-0/1 and massive degree-0/1/2 "
        "operator blocks are exported at two_j=5. This is a one-shell provider "
        "extension, not an all-shell provider or an identification with the "
        "separate hashed exact-T two_j<=138 stream. It does not bind two_j=5 to "
        "the feedback evaluator, evaluate any I_abc[5,k], select physical masses, "
        "close a tail or stopping rule, descend the quotient, restrict to the "
        "tangent cone, activate Bridge 3 or make a quantum claim."
    )
    return {
        "schema": "closed-universe-berger-recoil-first-omitted-shell-provider-two-j5-v1",
        "result_id": "BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5",
        "setting_id": values["detector_low"]["setting_id"],
        "claim_status": "DIRECT_RECOIL_INPUT_PROVIDER_EXTENDED_TO_FIRST_OMITTED_TWO_J5_SHELL_FEEDBACK_BINDING_OPEN",
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
            "boundaries": "h0<D0<h1<D1 compact windows; no spatial boundary",
            "charge_sector": "fixed-coupling Berger sector",
            "carrier": "direct advanced-Maxwell detector polynomials and exact Maxwell/massive de Rham kernel blocks",
            "degree": "Maxwell 0,1 and massive de Rham 0,1,2",
            "parity": "D0 axial and D1 transverse detector polarizations",
            "ell": "first omitted direct-provider shell two_j=5",
            "m": "all six representation rows",
            "k": "all six passive representation columns",
            "omega": "order-five corresponding-window and D1/h0 entire-series remainders with symbolic positive massive mass squared",
        },
        "carrier_crosswalk": {
            "source_carrier": "certified direct two_j=0,...,4 polynomial and exact-kernel payload",
            "target_carrier": "direct two_j=5 polynomial and exact-kernel payload",
            "map": "apply the identical content-addressed generic profile-moment, de Rham and series-coefficient functions at two_j=5",
            "detector_generator_source_hash_matches_import": detector_source_hash_matches,
            "cross_window_generator_source_hash_matches_import": cross_source_hash_matches,
            "kernel_generator_source_hash_matches_import": kernel_source_hash_matches,
            "hashed_exact_T_two_j138_stream_identification_status": "NO_CERTIFIED_MAP",
        },
        "support_audit": {
            "time_coordinate": "physical Berger time t with dTheta/dt=3/4",
            "formula": "tau_max=detector_support_upper-switch_support_lower",
            "rows": [
                {
                    "window": window,
                    "detector_support_upper": str(
                        detector_supports[window[:2]][1]
                    ),
                    "switch_support_lower": str(
                        switch_supports["h_" + window[-1]][0]
                    ),
                    "derived_tau_max": str(derived_tau_max[window]),
                    "matches_remainder_input": True,
                }
                for window in ("D0_on_h0", "D1_on_h1", "D1_on_h0")
            ],
        },
        "detector_provider_extension": {
            "two_j": TWO_J,
            "detectors": detector_rows,
            "D1_on_h0_cross_window_remainder": cross_remainder,
        },
        "kernel_provider_extension": {
            "two_j": TWO_J,
            "blocks": kernel_rows,
        },
        "mutation_results": [
            {
                "name": "reuse_D1_h1_remainder_on_h0",
                "detected": cross_remainder
                != detector_rows[1]["corresponding_window_remainder"],
            },
            {
                "name": "flip_two_j5_kernel_series_sign",
                "detected": wrong_sign[
                    "recurrence_defect_count_through_order4"
                ]
                > 0,
            },
        ],
        "flags": {
            "DIRECT_DETECTOR_POLYNOMIAL_PROVIDER_TWO_J5_EXPORTED": True,
            "D1_H0_CROSS_WINDOW_REMAINDER_TWO_J5_EXPORTED": True,
            "MAXWELL_AND_MASSIVE_KERNEL_BLOCKS_TWO_J5_EXPORTED": True,
            "TWO_J4_TO_TWO_J5_DIRECT_CARRIER_CROSSWALK_CERTIFIED": True,
            "HASHED_EXACT_T_TWO_J138_STREAM_IDENTIFIED_WITH_DIRECT_PROVIDER": False,
            "TWO_J5_FEEDBACK_CHANNELS_EVALUATED": False,
            "COMPLETE_ALL_SHELL_PROVIDER_EXPORTED": False,
            "TAIL_AWARE_STOP_LOOP_EXPORTED": False,
            "PHYSICAL_MASS_SPECIALIZATION_EXPORTED": False,
            "QUANTUM_CLAIM": False,
        },
        "next_gate": "BIND_ALL_EIGHT_TWO_J5_CHANNELS_TO_THE_PARTITIONED_FEEDBACK_BACKEND",
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
        raise SystemExit("first-omitted-shell provider certificate drift")
    print("BERGER_RECOIL_FIRST_OMITTED_SHELL_PROVIDER_TWO_J5 generation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
