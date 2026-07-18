"""Exact Diff x Weyl scalar Faddeev--Popov reduction on a 4d Einstein background.

This calculation closes the rank-two longitudinal-diffeomorphism/Weyl ghost
operator block to the single differential scalar determinant appearing in the
standard conformal-spin-two factorization.  It deliberately does not infer the
York/Hodge measure, nonminimal Berezinian, zero-mode policy, or the remaining
repository determinant rows.
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
STANDARD = HERE / "certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json"
CLASSICAL = ROOT / "quantum-weyl/classical_import/certificates/CLASSICAL_MINIMAL_BV_ANTIFIELD_IMPORT_V2.json"
OUTPUT = HERE / "certificates/DIFF_WEYL_SCALAR_GHOST_REDUCTION.json"
SCHEMA = HERE / "schema/diff-weyl-scalar-ghost-reduction-v1.schema.json"
SOURCE_PATHS = (
    "quantum-weyl/spectral/euclidean/scalar_ghost_reduction.py",
    "quantum-weyl/spectral/euclidean/verify_scalar_ghost_reduction.py",
    "quantum-weyl/spectral/euclidean/schema/diff-weyl-scalar-ghost-reduction-v1.schema.json",
    "quantum-weyl/spectral/euclidean/tests/test_scalar_ghost_reduction.py",
    "quantum-weyl/reports/diff-weyl-scalar-ghost-reduction.md",
)

Monomial = tuple[int, int]  # powers of (lambda, R)
Polynomial = dict[Monomial, Fraction]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _poly_add(*terms: Mapping[Monomial, Fraction]) -> Polynomial:
    result: Polynomial = {}
    for term in terms:
        for monomial, coefficient in term.items():
            result[monomial] = result.get(monomial, Fraction(0)) + coefficient
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def _poly_scale(value: Mapping[Monomial, Fraction], scalar: Fraction) -> Polynomial:
    return {
        monomial: coefficient * scalar
        for monomial, coefficient in value.items()
        if coefficient * scalar
    }


def _poly_mul(left: Mapping[Monomial, Fraction], right: Mapping[Monomial, Fraction]) -> Polynomial:
    result: Polynomial = {}
    for (ll, lr), lc in left.items():
        for (rl, rr), rc in right.items():
            monomial = (ll + rl, lr + rr)
            result[monomial] = result.get(monomial, Fraction(0)) + lc * rc
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def _payload(value: Mapping[Monomial, Fraction]) -> list[dict[str, int]]:
    return [
        {
            "lambda_degree": monomial[0],
            "R_degree": monomial[1],
            "numerator": coefficient.numerator,
            "denominator": coefficient.denominator,
        }
        for monomial, coefficient in sorted(value.items())
    ]


def scalar_fp_identity(
    *,
    beta: Fraction = Fraction(1, 4),
    ricci_pair_coefficient: Fraction = Fraction(1, 2),
) -> dict[str, Any]:
    """Return the exact scalar ghost matrix and determinant.

    ``lambda`` denotes the positive scalar Laplacian ``Delta_0=-nabla^2`` and
    ``R`` the scalar curvature.  The Einstein identity is
    ``Ric=(R/4)g``.  Two Ricci contributions in ``delta F`` give the default
    coefficient ``R/2``.  ``ricci_pair_coefficient`` is exposed solely for a
    mutation control.
    """

    lam: Polynomial = {(1, 0): Fraction(1)}
    curvature: Polynomial = {(0, 1): Fraction(1)}
    one: Polynomial = {(0, 0): Fraction(1)}

    longitudinal = _poly_add(
        _poly_scale(lam, -(Fraction(2) - Fraction(2) * beta)),
        _poly_scale(curvature, ricci_pair_coefficient),
    )
    weyl_mixing = _poly_scale(one, Fraction(2) * (Fraction(1) - Fraction(4) * beta))
    trace_from_longitudinal = _poly_scale(lam, Fraction(-2))
    trace_from_weyl = _poly_scale(one, Fraction(8))
    determinant = _poly_add(
        _poly_mul(longitudinal, trace_from_weyl),
        _poly_scale(_poly_mul(weyl_mixing, trace_from_longitudinal), Fraction(-1)),
    )
    target = _poly_add(lam, _poly_scale(curvature, Fraction(-1, 3)))
    residual = _poly_add(determinant, _poly_scale(target, Fraction(12)))
    return {
        "beta": {"numerator": beta.numerator, "denominator": beta.denominator},
        "matrix": {
            "longitudinal_gauge_from_xi_scalar": _payload(longitudinal),
            "longitudinal_gauge_from_weyl_ghost": _payload(weyl_mixing),
            "trace_gauge_from_xi_scalar": _payload(trace_from_longitudinal),
            "trace_gauge_from_weyl_ghost": _payload(trace_from_weyl),
        },
        "determinant": _payload(determinant),
        "target_scalar_operator": _payload(target),
        "proportionality_constant": -12,
        "target_residual": _payload(residual),
        "triangular": not weyl_mixing,
        "verified": not residual,
    }


def _validate_inputs() -> tuple[dict[str, Any], dict[str, Any]]:
    standard = json.loads(STANDARD.read_text())
    classical = json.loads(CLASSICAL.read_text())
    factors = standard.get("coefficient_calculation", {}).get(
        "constant_curvature_factor_ledger", []
    )
    scalar = next((row for row in factors if row.get("factor_id") == "ghost_depth_0"), None)
    if not (
        scalar
        and scalar.get("spin") == 0
        and scalar.get("M_squared") == -4
        and scalar.get("determinant_sign") == -1
        and standard.get("claim_flags", {}).get("STANDARD_BACKGROUND_A_AND_C_COMPUTED")
        is True
    ):
        raise ValueError("standard scalar ghost target drifted")
    if not (
        classical.get("claim_flags", {}).get("CLASSICAL_ANTIFIELD_EXPORT_IMPORTED")
        is True
        and classical.get("imported_export", {}).get("generator_count") == 6
        and classical.get("imported_export", {}).get("atom_count") == 18
    ):
        raise ValueError("classical minimal Diff x Weyl import drifted")
    return standard, classical


def build() -> dict[str, Any]:
    standard, classical = _validate_inputs()
    identity = scalar_fp_identity()
    alternate_beta = scalar_fp_identity(beta=Fraction(0))
    mutant = scalar_fp_identity(ricci_pair_coefficient=Fraction(1, 4))
    if not identity["verified"] or not identity["triangular"]:
        raise AssertionError("canonical scalar ghost reduction failed")
    if not alternate_beta["verified"] or mutant["verified"]:
        raise AssertionError("scalar ghost gauge/mutation controls failed")
    proof_payload = {
        "dependencies": {"standard": _sha256(STANDARD), "classical": _sha256(CLASSICAL)},
        "identity": identity,
        "alternate_beta": alternate_beta,
        "mutant": mutant,
    }
    certificate = {
        "schema": "quantum-weyl-diff-weyl-scalar-ghost-reduction-v1",
        "result_id": "DIFF_WEYL_SCALAR_GHOST_REDUCTION",
        "result_state": "SCALAR_FP_RANK_TWO_TO_ONE_DIFFERENTIAL_FACTOR_VERIFIED_FULL_BV_MEASURE_MAP_OPEN",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": classical["classical_commit"],
        "dependency_hashes": {
            "standard_spin2_factorization": _sha256(STANDARD),
            "classical_minimal_BV_import": _sha256(CLASSICAL),
        },
        "background": {
            "dimension": 4,
            "signature": "EUCLIDEAN",
            "geometry": "Einstein",
            "ricci_identity": "Ric_mu_nu=(R/4)g_mu_nu",
            "laplacian_convention": "Delta_0=-nabla^2",
        },
        "gauge_conventions": {
            "metric_BRST_row": "Q g_mu_nu=nabla_mu xi_nu+nabla_nu xi_mu+2 omega g_mu_nu",
            "vector_gauge": "F_mu=nabla^nu h_mu_nu-(1/4)nabla_mu h",
            "trace_gauge": "F_W=h",
            "ghost_inputs": ["xi_longitudinal_scalar", "omega"],
            "scalar_outputs": ["longitudinal_part_of_F_mu", "F_W"],
        },
        "exact_variation": {
            "vector_gauge_general_beta": "delta F_mu=Box xi_mu+Ric_mu_nu xi^nu+(1-2 beta)nabla_mu div(xi)+2(1-4 beta)nabla_mu omega",
            "gradient_commutator": "Box nabla_mu c=nabla_mu Box c+Ric_mu_nu nabla^nu c",
            "canonical_longitudinal_row": "-(3/2)nabla_mu(Delta_0-R/3)c",
            "canonical_trace_row": "-2 Delta_0 c+8 omega",
            "weyl_decoupling_from_vector_gauge": True,
        },
        "scalar_matrix_identity": identity,
        "gauge_parameter_control": {
            "beta_zero_matrix": alternate_beta,
            "determinant_independent_of_beta": True,
            "canonical_beta_selected_for_triangularity": "1/4",
        },
        "target_match": {
            "standard_factor_id": "ghost_depth_0",
            "standard_spin": 0,
            "standard_M_squared_at_R_12": -4,
            "repository_scalar_operator": "Delta_0-R/3",
            "unit_curvature_specialization": "R=12 gives Delta_0-4",
            "differential_input_rank": 2,
            "differential_output_factor_rank": 1,
            "remaining_factor": "operator-independent algebraic constant -12; functional-measure normalization open",
            "status": "EXACT_OPERATOR_AND_RANK_MATCH",
        },
        "negative_control": {
            "mutation": "drop one of the two Einstein Ricci contributions in the longitudinal row",
            "mutated_ricci_coefficient": "R/4",
            "mutated_identity": mutant,
            "rejected": True,
        },
        "claim_flags": {
            "DIFF_WEYL_SCALAR_FP_MATRIX_DERIVED": True,
            "SCALAR_GHOST_DIFFERENTIAL_RANK_TWO_TO_ONE": True,
            "STANDARD_SCALAR_GHOST_OPERATOR_MATCHED": True,
            "SCALAR_BLOCK_GAUGE_PARAMETER_DETERMINANT_INVARIANCE": True,
            "YORK_HODGE_MEASURE_MATCHED": False,
            "NONMINIMAL_BEREZINIAN_MATCHED": False,
            "FULL_REPOSITORY_HESSIAN_MATCHED": False,
            "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED": False,
            "REGULATED_SLAVNOV_BREAKING_COMPUTED": False,
            "QME_DISPOSITION": False,
        },
        "minimal_missing_carrier": {
            "closed_gap": "rank-two longitudinal Diff/Weyl scalar FP operator reduces exactly to the rank-one standard differential factor",
            "remaining_gap": "York/Hodge measure, antighost-multiplier and nonminimal Berezinian, physical repository Hessian normalization, zero modes, contour, and total row/factor map",
            "next_required_artifact": "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER",
        },
        "proof_sha256": _canonical_hash(proof_payload),
        "next_gate": "MATCH_YORK_HODGE_MEASURE_NONMINIMAL_BEREZINIAN_AND_REPOSITORY_HESSIAN_ROWS",
        "claim_boundary": (
            "This exact LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL result derives the two-by-two longitudinal-diffeomorphism/Weyl Faddeev--Popov scalar block on a four-dimensional Einstein background. In the conformally invariant vector gauge it is triangular and its determinant is -12 times Delta_0-R/3, so the two scalar ghost inputs yield exactly the one differential rank-one standard ghost factor with mass shift -4 at R=12; the remaining multiplier is operator independent, but its infinite-dimensional measure normalization is open. It does not compute the York/Hodge functional measure, antighost/multiplier or nonminimal Berezinian, the complete repository Hessian, zero modes, contours, anomaly coefficients, a regulated Slavnov breaking, QME disposition, D-Cartan class, residual transfer, or Lorentzian quantum theory."
        ),
        "provenance": {
            "source_sha256": {path: _sha256(ROOT / path) for path in SOURCE_PATHS}
        },
    }
    validate_claim_boundary(certificate)
    return certificate


def validate_claim_boundary(value: dict[str, Any]) -> None:
    flags = value.get("claim_flags", {})
    required_true = (
        "DIFF_WEYL_SCALAR_FP_MATRIX_DERIVED",
        "SCALAR_GHOST_DIFFERENTIAL_RANK_TWO_TO_ONE",
        "STANDARD_SCALAR_GHOST_OPERATOR_MATCHED",
        "SCALAR_BLOCK_GAUGE_PARAMETER_DETERMINANT_INVARIANCE",
    )
    required_false = (
        "YORK_HODGE_MEASURE_MATCHED",
        "NONMINIMAL_BEREZINIAN_MATCHED",
        "FULL_REPOSITORY_HESSIAN_MATCHED",
        "REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER_ACCEPTED",
        "REGULATED_SLAVNOV_BREAKING_COMPUTED",
        "QME_DISPOSITION",
    )
    if any(flags.get(name) is not True for name in required_true) or any(
        flags.get(name) is not False for name in required_false
    ):
        raise ValueError("scalar ghost reduction crossed its claim boundary")


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
        raise SystemExit(f"stale scalar ghost reduction: {OUTPUT}")
    print("DIFF x WEYL SCALAR GHOST REDUCTION: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
