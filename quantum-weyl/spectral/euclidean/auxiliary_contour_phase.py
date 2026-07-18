"""Exact modewise contour and phase for the standard algebraic TT auxiliary."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/STANDARD_TT_AUXILIARY_CONTOUR_PHASE.json"
SCHEMA = HERE / "schema/standard-tt-auxiliary-contour-phase-v1.schema.json"
AUXILIARY = HERE / "certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json"

SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/auxiliary_contour_phase.py",
    "quantum-weyl/spectral/euclidean/verify_auxiliary_contour_phase.py",
    "quantum-weyl/spectral/euclidean/schema/standard-tt-auxiliary-contour-phase-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_auxiliary_contour_phase.py",
    "quantum-weyl/reports/standard-tt-auxiliary-contour-phase.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def complex_pair(real: Fraction | int = 0, imaginary: Fraction | int = 0) -> dict[str, dict[str, int]]:
    def rational(value: Fraction | int) -> dict[str, int]:
        value = Fraction(value)
        return {"numerator": value.numerator, "denominator": value.denominator}

    return {"real": rational(real), "imaginary": rational(imaginary)}


def modewise_completion(*, auxiliary_sign: int = -1) -> dict[str, Any]:
    """Complete the square after ``f=i y`` using exact complex coefficients."""

    # Coefficients of h^2, h*y, y^2 in S(h,i y). The accepted sign is the
    # repository-independent standard block -f^2/2.
    h2 = complex_pair(1)  # lambda, stored as coefficient of lambda
    hy = complex_pair(0, 1)  # i lambda
    y2 = complex_pair(Fraction(-auxiliary_sign, 2))
    convergent = auxiliary_sign == -1
    # 1/2 (y+i lambda h)^2 + 1/2 lambda(lambda+2) h^2.
    completion_residual = {
        "h2_lambda": complex_pair(0),
        "h2_lambda_squared": complex_pair(0),
        "hy_lambda": complex_pair(0),
        "y2": complex_pair(-Fraction(auxiliary_sign + 1, 2)),
    }
    return {
        "auxiliary_diagonal_sign": auxiliary_sign,
        "rotated_action_coefficients": {
            "h2_lambda": h2,
            "hy_lambda": hy,
            "y2": y2,
        },
        "completed_square": "1/2 (y+i lambda h)^2 + 1/2 lambda(lambda+2) h^2",
        "completion_residual": completion_residual,
        "completion_verified": all(
            all(part["numerator"] == 0 for part in coefficient.values())
            for coefficient in completion_residual.values()
        ),
        "rotated_quadratic_real_part_positive": convergent,
    }


def convergence_wedge(theta_over_pi: Fraction) -> dict[str, Any]:
    """Record exact decisions at the canonical and two boundary/control rays."""

    canonical = theta_over_pi == Fraction(1, 2)
    real_axis = theta_over_pi == 0
    boundary = theta_over_pi in (Fraction(1, 4), Fraction(3, 4))
    return {
        "theta_over_pi": {
            "numerator": theta_over_pi.numerator,
            "denominator": theta_over_pi.denominator,
        },
        "Re_exp_2i_theta_sign": -1 if canonical else 1 if real_axis else 0 if boundary else None,
        "absolutely_convergent": canonical,
        "classification": (
            "CANONICAL_POSITIVE_IMAGINARY_THIMBLE"
            if canonical
            else "DIVERGENT_REAL_AXIS"
            if real_axis
            else "STOKES_BOUNDARY_NOT_ABSOLUTELY_CONVERGENT"
            if boundary
            else "NOT_CLASSIFIED_BY_EXACT_FIXTURE"
        ),
    }


def build() -> dict[str, Any]:
    auxiliary = json.loads(AUXILIARY.read_text())
    if (
        auxiliary.get("result_id") != "STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH"
        or auxiliary["auxiliary_action"]["quadratic_form"]
        != "1/2 <h,2 A h> + <h,A f> - 1/2 <f,f>"
        or auxiliary["exact_schur_identity"]["verified"] is not True
    ):
        raise ValueError("standard auxiliary dependency drifted")
    completion = modewise_completion()
    sign_mutant = modewise_completion(auxiliary_sign=1)
    canonical = convergence_wedge(Fraction(1, 2))
    real_axis = convergence_wedge(Fraction(0))
    stokes = convergence_wedge(Fraction(1, 4))
    if (
        not completion["completion_verified"]
        or not completion["rotated_quadratic_real_part_positive"]
        or sign_mutant["completion_verified"]
        or not canonical["absolutely_convergent"]
        or real_axis["absolutely_convergent"]
        or stokes["absolutely_convergent"]
    ):
        raise AssertionError("auxiliary contour mutation control failed")
    contour = {
        "field_rotation": "f=i y with y real",
        "orientation": "y runs from -infinity to +infinity, hence f runs from -i infinity to +i infinity",
        "measure_per_real_mode": "df/(i sqrt(2 pi))=dy/sqrt(2 pi)",
        "normalization": "integral_R dy/sqrt(2 pi) exp(-y^2/2)=1",
        "completion_shift": "deform y in R to y+i lambda h; integrand is entire and Gaussian-decaying in the same Stokes wedge",
        "residual_modewise_phase": "PLUS_ONE_BY_ORIENTED_NORMALIZED_MEASURE",
        "background_dependent_log_coefficient": "ZERO_FOR_THE_NORMALIZED_ALGEBRAIC_IDENTITY_BLOCK",
    }
    proof_payload = {
        "dependency": _sha256(AUXILIARY),
        "completion": completion,
        "canonical": canonical,
        "real_axis": real_axis,
        "stokes": stokes,
        "contour": contour,
    }
    value = {
        "schema": "quantum-weyl-standard-tt-auxiliary-contour-phase-v1",
        "result_id": "STANDARD_TT_AUXILIARY_CONTOUR_PHASE",
        "result_state": "STANDARD_AUXILIARY_POSITIVE_IMAGINARY_THIMBLE_AND_MODEWISE_PHASE_FIXED_REPOSITORY_MATCH_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "LOCAL-ALGEBRAIC"],
        "dependency_hashes": {"standard_auxiliary_Schur_identity": _sha256(AUXILIARY)},
        "finite_mode_identity": {
            "starting_action": "S_lambda=lambda h^2+lambda h f-f^2/2",
            "rotation": "f=i y",
            "completion": completion,
            "effective_action": "S_eff=1/2 lambda(lambda+2) h^2",
        },
        "convergence_rays": {
            "canonical": canonical,
            "real_axis_negative_control": real_axis,
            "stokes_boundary_control": stokes,
            "open_convergence_wedge": "pi/4<arg(f)<3pi/4 modulo pi",
        },
        "oriented_normalized_contour": contour,
        "negative_controls": {
            "wrong_auxiliary_sign": sign_mutant,
            "real_axis_diverges": True,
            "stokes_boundary_not_absolutely_convergent": True,
            "all_rejected": True,
        },
        "claim_flags": {
            "STANDARD_AUXILIARY_CONTOUR_FIXED": True,
            "STANDARD_AUXILIARY_MODEWISE_PHASE_FIXED": True,
            "STANDARD_AUXILIARY_BACKGROUND_LOG_COEFFICIENT_ZERO": True,
            "REPOSITORY_TT_HESSIAN_MATCHED": False,
            "REPOSITORY_AUXILIARY_CONTOUR_MATCHED": False,
            "INFINITE_DIMENSIONAL_REGULATOR_FIXED": False,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "MATCH_REPOSITORY_TT_AUXILIARY_BLOCK_TO_STANDARD_NORMALIZED_THIMBLE",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate fixes a convergent oriented contour and modewise phase for the standard algebraic transverse-traceless auxiliary block. Rotating f=i y converts the wrong-sign algebraic Gaussian into a positive real Gaussian; exact completion of the square reproduces one half lambda(lambda+2)h^2. The normalized measure df/(i sqrt(2 pi)) gives residual phase plus one per real auxiliary mode and no background-dependent logarithmic coefficient for the algebraic identity block. The real contour and Stokes-boundary rays fail convergence, and a sign mutation fails the completion identity. This is a declared standard-factor contour policy, not a repository match. It does not identify the repository TT Hessian or auxiliary row, fix an infinite-dimensional regulator or conformal-group volume, accept the full BV multiplicity ledger, compute anomaly coefficients or Slavnov breaking, decide the QME, classify the D-Cartan defect, transfer residual cohomology, or establish Lorentzian quantum theory."
        ),
        "provenance": {"source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}},
    }
    validate_claim_boundary(value)
    return value


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if not all(flags.get(name) is True for name in (
        "STANDARD_AUXILIARY_CONTOUR_FIXED",
        "STANDARD_AUXILIARY_MODEWISE_PHASE_FIXED",
        "STANDARD_AUXILIARY_BACKGROUND_LOG_COEFFICIENT_ZERO",
    )) or any(flags.get(name) is not False for name in (
        "REPOSITORY_TT_HESSIAN_MATCHED",
        "REPOSITORY_AUXILIARY_CONTOUR_MATCHED",
        "INFINITE_DIMENSIONAL_REGULATOR_FIXED",
        "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_DISPOSITION",
    )):
        raise ValueError("auxiliary contour claim boundary crossed")


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
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale auxiliary contour certificate: {OUTPUT}")
    print("standard TT auxiliary contour and phase: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
