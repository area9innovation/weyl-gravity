"""Exact auxiliary/fourth-order Schur identity for the standard spin-two factor.

The calculation closes the algebraic Gaussian identity behind the two
physical transverse spin-two determinant factors.  It does not identify the
repository gauge-fixed operator or select an auxiliary contour/measure.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
COEFFICIENT = HERE / "certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json"
OUTPUT = HERE / "certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json"
SCHEMA = HERE / "schema/standard-spin2-auxiliary-fourth-order-match-v1.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/auxiliary_fourth_order_match.py",
    "quantum-weyl/spectral/euclidean/verify_auxiliary_fourth_order_match.py",
    "quantum-weyl/spectral/euclidean/schema/standard-spin2-auxiliary-fourth-order-match-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_auxiliary_fourth_order_match.py",
    "quantum-weyl/reports/standard-spin2-auxiliary-fourth-order-match.md",
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _poly_add(*terms: Mapping[int, Fraction]) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for term in terms:
        for degree, coefficient in term.items():
            result[degree] = result.get(degree, Fraction(0)) + coefficient
    return {degree: coefficient for degree, coefficient in result.items() if coefficient}


def _poly_mul(left: Mapping[int, Fraction], right: Mapping[int, Fraction]) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for left_degree, left_coefficient in left.items():
        for right_degree, right_coefficient in right.items():
            degree = left_degree + right_degree
            result[degree] = result.get(degree, Fraction(0)) + left_coefficient * right_coefficient
    return {degree: coefficient for degree, coefficient in result.items() if coefficient}


def _poly_scale(value: Mapping[int, Fraction], scalar: Fraction) -> dict[int, Fraction]:
    return {degree: scalar * coefficient for degree, coefficient in value.items() if scalar * coefficient}


def _poly_payload(value: Mapping[int, Fraction]) -> list[dict[str, int]]:
    return [
        {
            "degree": degree,
            "numerator": coefficient.numerator,
            "denominator": coefficient.denominator,
        }
        for degree, coefficient in sorted(value.items())
    ]


def schur_identity(*, mass_gap: Fraction = Fraction(2), top_left_shift: Fraction | None = None) -> dict[str, Any]:
    """Compute the exact eigenvalue-polynomial block and Schur determinants."""

    lam = {1: Fraction(1)}
    one = {0: Fraction(1)}
    shift = mass_gap if top_left_shift is None else top_left_shift
    k_hh = _poly_scale(lam, shift)
    k_hf = lam
    k_ff = _poly_scale(one, Fraction(-1))

    # det [[shift*lambda, lambda], [lambda, -1]].
    block_determinant = _poly_add(
        _poly_mul(k_hh, k_ff),
        _poly_scale(_poly_mul(k_hf, k_hf), Fraction(-1)),
    )
    target = _poly_mul(lam, _poly_add(lam, {0: mass_gap}))
    schur_complement = _poly_add(k_hh, _poly_mul(k_hf, k_hf))
    signed_target = _poly_scale(target, Fraction(-1))
    residual = _poly_add(block_determinant, target)
    schur_residual = _poly_add(schur_complement, _poly_scale(target, Fraction(-1)))
    return {
        "mass_gap": {
            "numerator": mass_gap.numerator,
            "denominator": mass_gap.denominator,
        },
        "block_entries": {
            "K_hh": _poly_payload(k_hh),
            "K_hf": _poly_payload(k_hf),
            "K_fh": _poly_payload(k_hf),
            "K_ff": _poly_payload(k_ff),
        },
        "block_determinant": _poly_payload(block_determinant),
        "minus_fourth_order_target": _poly_payload(signed_target),
        "schur_complement": _poly_payload(schur_complement),
        "fourth_order_target": _poly_payload(target),
        "determinant_residual": _poly_payload(residual),
        "schur_residual": _poly_payload(schur_residual),
        "verified": not residual and not schur_residual,
    }


def _validate_dependency(value: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    flags = value.get("claim_flags", {})
    calculation = value.get("coefficient_calculation", {})
    factors = calculation.get("constant_curvature_factor_ledger", [])
    by_id = {row.get("factor_id"): row for row in factors}
    if (
        value.get("result_state")
        != "STANDARD_SPIN2_BACKGROUND_COEFFICIENTS_COMPUTED_D_PULLBACK_CERTIFIED"
        or flags.get("STANDARD_BACKGROUND_A_AND_C_COMPUTED") is not True
        or flags.get("STANDARD_BACKGROUND_PARITY_ODD_ZERO_VERIFIED") is not True
        or set(by_id) != {
            "physical_depth_0",
            "ghost_depth_0",
            "physical_depth_1",
            "ghost_depth_1",
        }
    ):
        raise ValueError("standard determinant dependency drifted")
    lower = by_id["physical_depth_1"]
    upper = by_id["physical_depth_0"]
    if (
        lower.get("spin") != 2
        or lower.get("M_squared") != 2
        or upper.get("spin") != 2
        or upper.get("M_squared") != 4
        or lower.get("determinant_sign") != 1
        or upper.get("determinant_sign") != 1
    ):
        raise ValueError("physical spin-two factor pair drifted")
    return lower, upper


def build() -> dict[str, Any]:
    coefficient = json.loads(COEFFICIENT.read_text())
    lower, upper = _validate_dependency(coefficient)
    identity = schur_identity()
    mutant = schur_identity(top_left_shift=Fraction(3))
    if not identity["verified"] or mutant["verified"]:
        raise AssertionError("auxiliary/fourth-order mutation control failed")
    proof_payload = {
        "dependency": _sha256(COEFFICIENT),
        "identity": identity,
        "mutant_residual": mutant["determinant_residual"],
    }
    certificate = {
        "schema": "quantum-weyl-standard-spin2-auxiliary-fourth-order-match-v1",
        "result_id": "STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH",
        "result_state": "STANDARD_PHYSICAL_TT_SCHUR_AND_LOCAL_JACOBIAN_IDENTITY_VERIFIED_REPOSITORY_MATCH_OPEN",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL", "LOCAL-ALGEBRAIC"],
        "dependency_hashes": {
            "standard_coefficient_certificate": _sha256(COEFFICIENT),
        },
        "factor_match": {
            "bundle": "real transverse traceless symmetric rank-two tensors",
            "lower_factor_id": lower["factor_id"],
            "lower_factor": "A=Delta_2_perp(2)",
            "upper_factor_id": upper["factor_id"],
            "upper_factor": "A+2=Delta_2_perp(4)",
            "commutation_reason": "the factors differ by the scalar endomorphism 2 identity",
            "fourth_order_operator": "A(A+2)",
        },
        "auxiliary_action": {
            "fields": ["h_TT", "f_TT"],
            "quadratic_form": "1/2 <h,2 A h> + <h,A f> - 1/2 <f,f>",
            "auxiliary_equation": "f=A h",
            "substituted_action": "1/2 <h,A(A+2)h>",
            "locality": "SECOND_ORDER_IN_h_AND_ALGEBRAIC_IN_f_DIAGONAL",
        },
        "exact_schur_identity": identity,
        "gaussian_measure_ledger": {
            "block_determinant_identity": "det K=det(-I_f) det[A(A+2)]",
            "field_dependent_jacobian": "NONE_FOR_TRANSLATION_INVARIANT_NORMALIZED_ALGEBRAIC_f_MEASURE",
            "local_logarithmic_coefficient_from_det_minus_identity": "ZERO_BACKGROUND_DEPENDENCE",
            "contour_phase": "NOT_FIXED",
            "finite_normalization": "NOT_FIXED",
            "repository_measure_match": "NOT_COMPUTED",
        },
        "negative_control": {
            "mutation": "replace K_hh=2A by K_hh=3A",
            "determinant_residual": mutant["determinant_residual"],
            "schur_residual": mutant["schur_residual"],
            "rejected": True,
        },
        "claim_flags": {
            "STANDARD_PHYSICAL_TT_AUXILIARY_SCHUR_IDENTITY": True,
            "STANDARD_LOCAL_FIELD_DEPENDENT_JACOBIAN_ZERO": True,
            "FULL_GHOST_AND_NONMINIMAL_OPERATOR_MATCH": False,
            "REPOSITORY_AUXILIARY_MEASURE_MATCH": False,
            "REPOSITORY_ELLIPTIC_COMPLEX_CERTIFIED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "minimal_missing_carrier": {
            "status": "REPOSITORY_OPERATOR_NORMALIZATION_CONTOUR_AND_FULL_BV_ROW_MATCH_OPEN",
            "standard_physical_TT_algebraic_identity_gap": False,
            "required_output": "identify the repository gauge-fixed physical Hessian with A(A+2), match every ghost/nonminimal row and normalize the algebraic auxiliary measure and contour",
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "MATCH_REPOSITORY_FULL_BV_ELLIPTIC_OPERATOR_MULTIPLICITIES_MEASURE_AND_CONTOUR",
        "claim_boundary": (
            "This exact EUCLIDEAN-SPECTRAL plus LOCAL-ALGEBRAIC preflight proves the local Schur-complement and block-determinant identity relating the two standard physical transverse-traceless spin-two factors Delta_2(2) Delta_2(4) to a second-order/algebraic auxiliary quadratic form. Under a translation-invariant normalized algebraic auxiliary measure, det(-I_f) has no background-dependent logarithmic coefficient. The repository physical Hessian, all ghost and nonminimal rows, action normalization, auxiliary contour, finite phase, zero modes, determinant measure and regulated Slavnov functional remain unmatched. No repository coefficient, elliptic certificate, QME disposition, Cartan classification, residual transfer or Lorentzian theorem is claimed."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    validate_claim_boundary(certificate)
    return certificate


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    if (
        flags.get("STANDARD_PHYSICAL_TT_AUXILIARY_SCHUR_IDENTITY") is not True
        or flags.get("STANDARD_LOCAL_FIELD_DEPENDENT_JACOBIAN_ZERO") is not True
        or any(
            flags.get(name) is not False
            for name in (
                "FULL_GHOST_AND_NONMINIMAL_OPERATOR_MATCH",
                "REPOSITORY_AUXILIARY_MEASURE_MATCH",
                "REPOSITORY_ELLIPTIC_COMPLEX_CERTIFIED",
                "REGULATED_SLAVNOV_BREAKING_COMPUTED",
                "QME_DISPOSITION",
            )
        )
    ):
        raise ValueError("auxiliary/fourth-order preflight crossed its claim boundary")


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
        raise SystemExit(f"stale auxiliary/fourth-order match: {OUTPUT}")
    print("STANDARD SPIN2 AUXILIARY/FOURTH-ORDER MATCH: SCHUR IDENTITY PASS; REPOSITORY MATCH OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
