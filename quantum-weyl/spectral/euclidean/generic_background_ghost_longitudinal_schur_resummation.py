#!/usr/bin/env python3
"""Resum every longitudinal Diff--Weyl ghost carrier into one Schur factor."""

from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any

import sympy as sp
from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "certificates/GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION.json"
SCHEMA = HERE / "schema/generic-background-ghost-longitudinal-schur-resummation-v1.schema.json"
DEPENDENCIES = {
    "Hodge_resolvent_reduction": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json",
    "vector_CPT_projection": HERE
    / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_CPT_PROJECTION.json",
    "ghost_operator": HERE
    / "certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _reference(path: Path) -> dict[str, str]:
    value = json.loads(path.read_text())
    return {
        "path": str(path.relative_to(ROOT)),
        "result_id": str(value.get("result_id") or value.get("schema")),
        "sha256": _sha256(path),
    }


def _q(value: sp.Expr | Fraction | int) -> dict[str, int]:
    rational = sp.Rational(value)
    return {"numerator": int(rational.p), "denominator": int(rational.q)}


def _trace(matrix: sp.Matrix) -> sp.Expr:
    return sp.trace(matrix)


def _fixture() -> dict[str, Any]:
    delta0 = sp.diag(2, 3)
    d = sp.Matrix([[1, 0], [0, 1], [0, 0], [0, 0]])
    delta = sp.Matrix([[2, 0, 0, 0], [0, 3, 0, 0]])
    f = sp.diag(2, 3, 1, 1)
    f[2:4, 2:4] = sp.Matrix([[5, 1], [1, 7]])
    w = sp.Matrix(
        [
            [1, 2, -1, 3],
            [2, -2, 4, 1],
            [-1, 4, 3, 2],
            [3, 1, 2, -1],
        ]
    )
    if delta * d != delta0 or f * d != d * delta0 or delta * f != delta0 * delta:
        raise AssertionError("finite Schur fixture violates the Hodge Ward identities")
    g = f.inv()
    h0 = f + sp.Rational(1, 2) * d * delta
    a = f + w
    h = a + sp.Rational(1, 2) * d * delta
    schur = sp.Rational(2, 3) * sp.eye(2) + sp.Rational(1, 3) * delta * a.inv() * d
    determinant_residual = sp.factor(
        h.det() / h0.det() - (a.det() / f.det()) * schur.det()
    )
    if determinant_residual != 0:
        raise AssertionError("normalized scalar Schur determinant identity failed")

    b1 = delta0.inv() * delta * w * d * delta0.inv()
    b2 = delta0.inv() * delta * w * g * w * d * delta0.inv()
    b3 = delta0.inv() * delta * w * g * w * g * w * d * delta0.inv()
    direct = h0.inv() * w
    vector = g * w
    direct_coefficients = (
        _trace(direct),
        -sp.Rational(1, 2) * _trace(direct**2),
        sp.Rational(1, 3) * _trace(direct**3),
    )
    vector_coefficients = (
        _trace(vector),
        -sp.Rational(1, 2) * _trace(vector**2),
        sp.Rational(1, 3) * _trace(vector**3),
    )
    scalar_coefficients = (
        -sp.Rational(1, 3) * _trace(b1),
        sp.Rational(1, 3) * _trace(b2)
        - sp.Rational(1, 18) * _trace(b1**2),
        -sp.Rational(1, 3) * _trace(b3)
        + sp.Rational(1, 9) * _trace(b1 * b2)
        - sp.Rational(1, 81) * _trace(b1**3),
    )
    if any(
        sp.factor(direct_row - vector_row - scalar_row) != 0
        for direct_row, vector_row, scalar_row in zip(
            direct_coefficients, vector_coefficients, scalar_coefficients
        )
    ):
        raise AssertionError("cubic scalar Schur trace expansion failed")
    return {
        "vector_dimension": 4,
        "scalar_dimension": 2,
        "Ward_identities_verified": ["delta d=Delta0", "F d=d Delta0", "delta F=Delta0 delta"],
        "determinant_identity_residual": _q(determinant_residual),
        "direct_log_coefficients_through_W3": [_q(value) for value in direct_coefficients],
        "vector_plus_scalar_coefficients_through_W3": [
            _q(vector_row + scalar_row)
            for vector_row, scalar_row in zip(vector_coefficients, scalar_coefficients)
        ],
        "noncommuting_W": [[_q(value) for value in row] for row in w.tolist()],
    }


def _einstein_identity() -> dict[str, str]:
    x, lam = sp.symbols("x lambda", nonzero=True)
    schur = sp.factor(sp.Rational(2, 3) + sp.Rational(1, 3) * x / (x - 2 * lam))
    product = sp.factor((x - 2 * lam) * schur / x)
    if sp.factor(schur - (x - sp.Rational(4, 3) * lam) / (x - 2 * lam)) != 0:
        raise AssertionError("Einstein Schur factor failed")
    if sp.factor(product - (x - sp.Rational(4, 3) * lam) / x) != 0:
        raise AssertionError("Einstein scalar ghost factor failed")
    return {
        "Ricci_specialization": "Ric=(R/4)g and W=-(R/2)I",
        "minimal_vector_longitudinal_ratio": "(Delta0-R/2)/Delta0",
        "normalized_Schur_factor": "(Delta0-R/3)/(Delta0-R/2)",
        "product": "(Delta0-R/3)/Delta0",
        "accepted_scalar_factor": "Delta0-R/3",
    }


def build() -> dict[str, Any]:
    values = {name: json.loads(path.read_text()) for name, path in DEPENDENCIES.items()}
    hodge = values["Hodge_resolvent_reduction"]
    vector = values["vector_CPT_projection"]
    ghost = values["ghost_operator"]
    if (
        hodge.get("proper_time_to_resolvent", {}).get("resolvent_identity")
        != "G_H0=G_F-(1/3)d Delta_0^-2 delta"
        or vector.get("claim_flags", {}).get(
            "GENERIC_GHOST_VECTOR_N1_PLUS_N2_CPT_PROJECTION_COMPUTED"
        )
        is not True
        or ghost.get("generic_Hodge_mixing", {}).get(
            "Einstein_scalar_factor_reproduced"
        )
        != "Delta_0-R/3"
    ):
        raise ValueError("longitudinal Schur dependencies drifted")

    result = {
        "schema": "quantum-weyl-generic-background-ghost-longitudinal-schur-resummation-v1",
        "result_id": "GENERIC_BACKGROUND_GHOST_LONGITUDINAL_SCHUR_RESUMMATION",
        "result_state": "THREE_LONGITUDINAL_DW_CARRIERS_RESUMMED_TO_ONE_NORMALIZED_SCALAR_SCHUR_FACTOR_WITH_REGULATOR_BOUNDARY",
        "lifecycle_state": "GENERIC_SCHUR_OPERATOR_DERIVED_RELATIVE_DETERMINANT_KERNEL_UNEVALUATED",
        "dependency_tags": ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        "classical_commit": hodge["classical_commit"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "mode_domain": "primed nonzero ghost modes on a compact manifold without boundary",
            "operator_scope": "generic-background Diff-Weyl ghost determinant relative to the Endo base",
        },
        "operator_dictionary": {
            "minimal_vector_operator": "A=F+W with F=-Box I+Ric and W=-2 Ric",
            "full_positive_ghost_operator": "H=A+(1/2)d delta",
            "Endo_base": "H0=F+(1/2)d delta",
            "Ward_identities": ["F d=d Delta0", "delta F=Delta0 delta", "delta d=Delta0"],
        },
        "exact_determinant_factorization": {
            "matrix_determinant_lemma": "det(H)=det(A) det[I+(1/2)delta A^-1 d] in finite dimension, and for a common Fredholm determinant-class prescription",
            "base_scalar_factor": "I+(1/2)delta F^-1 d=(3/2)I",
            "normalized_scalar_Schur_operator": "S_L(W)=(2/3)I+(1/3)delta(F+W)^-1 d",
            "relative_identity": "Det_rel(H,H0)=Det_rel(F+W,F) Det_F(S_L(W),I) under one compatible determinant-class prescription",
            "principal_symbol": "sigma_0(S_L)=1",
            "first_correction_order": "pseudodifferential order -2 and curvature order one",
        },
        "regularization_boundary": {
            "finite_dimensional_identity": "EXACT",
            "Fredholm_relative_identity": "EXACT_IF_S_L_MINUS_I_AND_RELATIVE_RESOLVENTS_ARE_DETERMINANT_CLASS_IN_THE_DECLARED_COMMON_PRESCRIPTION",
            "generic_4d_trace_class_status": "ORDER_MINUS_TWO_DOES_NOT_PROVE_TRACE_CLASS_IN_DIMENSION_FOUR",
            "required_generic_determinant": "REGULARIZED_RELATIVE_DETERMINANT_OR_EQUIVALENT_COMMON_TRACE_REGULATOR",
            "zeta_multiplicative_anomaly": "LOCAL_TERM_NOT_EVALUATED",
            "nonlocal_consequence": "THE_THREE_DW_TRACE_LOG_TOWERS_ARE_ONE_SCHUR_SERIES; LOCAL_ZETA_ANOMALY_MAY_SHIFT_ONLY_LOCAL_COUNTERTERM_COORDINATES",
        },
        "resolvent_series": {
            "definition": "B_n=Delta0^-1 delta W (G_F W)^(n-1) d Delta0^-1",
            "Schur_series": "S_L=I+sum_(n>=1) (-1)^n B_n/3",
            "trace_log_through_W3": [
                {"W_order": 1, "terms": ["-(1/3)Tr(B1)"]},
                {"W_order": 2, "terms": ["+(1/3)Tr(B2)", "-(1/18)Tr(B1^2)"]},
                {"W_order": 3, "terms": ["-(1/3)Tr(B3)", "+(1/9)Tr(B1 B2)", "-(1/81)Tr(B1^3)"]},
            ],
            "Hodge_carrier_match": {
                "N1_LONGITUDINAL_SCALAR": "-(1/3)Tr(B1)",
                "N2_VECTOR_LONGITUDINAL": "+(1/3)Tr(B2)",
                "N2_LONGITUDINAL_LONGITUDINAL": "-(1/18)Tr(B1^2)",
                "completed_n3_longitudinal_coefficients": [
                    _q(Fraction(-1, 3)),
                    _q(Fraction(1, 9)),
                    _q(Fraction(-1, 81)),
                ],
            },
        },
        "Einstein_specialization": _einstein_identity(),
        "exact_noncommuting_fixture": _fixture(),
        "analytic_disposition": {
            "three_separate_DW_carrier_evaluations_required": False,
            "single_remaining_generic_kernel": "relative trace log det' S_L(W)",
            "operator_type": "elliptic scalar pseudodifferential operator of order zero with identity principal symbol",
            "smallest_missing_input": "same-regulator relative determinant kernel of S_L(W), equivalently covariant scalar/vector open-derivative kernels through cubic curvature order",
            "global_data": "primed inverse, boundary condition and relative determinant prescription remain required",
        },
        "claim_flags": {
            "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED": True,
            "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION": True,
            "EINSTEIN_SCALAR_GHOST_FACTOR_REPRODUCED_FROM_SCHUR_FACTOR": True,
            "ZETA_FACTORIZATION_WITHOUT_LOCAL_MULTIPLICATIVE_ANOMALY_PROVED": False,
            "ORDINARY_FREDHOLM_DETERMINANT_CLASS_PROVED": False,
            "GENERIC_LONGITUDINAL_SCHUR_FORM_FACTORS_COMPUTED": False,
            "ALL_FIVE_HODGE_RESOLVENT_CARRIERS_EVALUATED": False,
            "COMPLETE_GENERIC_GHOST_THIRD_CURVATURE_FUNCTIONS_COMPUTED": False,
            "PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "RESIDUAL_TRANSFER_AUTHORIZED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "dependencies": {name: _reference(path) for name, path in DEPENDENCIES.items()},
        "next_gate": "EVALUATE_NORMALIZED_LONGITUDINAL_SCHUR_RELATIVE_DETERMINANT_AND_GENERIC_PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL",
        "claim_boundary": (
            "This LOCAL-ALGEBRAIC plus EUCLIDEAN-SPECTRAL certificate uses the exact finite-dimensional matrix determinant lemma and the frozen Hodge Ward identities to resum every longitudinal D_W trace-log contribution to the generic Diff-Weyl ghost determinant into the single normalized scalar Schur operator S_L(W)=(2/3)I+(1/3)delta(F+W)^-1 d. Its trace-log expansion reproduces the three open n=1/n=2 coefficients and the completed n=3 longitudinal coefficients, an exact noncommuting fixture verifies the relative determinant through cubic order, and the Einstein specialization reproduces the accepted Delta0-R/3 scalar ghost factor. This is a formal trace-log factorization and resummation theorem, not an evaluation of the generic relative determinant kernel. Since S_L-I begins at pseudodifferential order -2 in dimension four, ordinary trace-class/Fredholm determinacy is not proved by order counting; a regularized relative determinant or equivalent common trace regulator is required. A zeta-factorized implementation can additionally carry a local multiplicative anomaly, which is explicitly unevaluated here. The generic Schur form factors, local multiplicative-anomaly term, full five-carrier ghost functions, physical fourth-order Hessian, complete repository functions or coefficients, Gamma1/Q1, residual transfer, Lorentzian QME, Hadamard, particle, positivity, scattering and unitarity claims remain open."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    flags = value["claim_flags"]
    true_flags = {
        "GENERIC_GHOST_LONGITUDINAL_SCHUR_FACTORIZATION_COMPUTED",
        "THREE_DW_CARRIERS_RESUMMED_IN_COMMON_RELATIVE_DETERMINANT_EXPANSION",
        "EINSTEIN_SCALAR_GHOST_FACTOR_REPRODUCED_FROM_SCHUR_FACTOR",
    }
    if any(flags[name] is not True for name in true_flags) or any(
        flag is not False for name, flag in flags.items() if name not in true_flags
    ):
        raise ValueError("longitudinal Schur resummation crossed its claim boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale longitudinal Schur resummation: {OUTPUT}")
    print("GENERIC GHOST LONGITUDINAL SCHUR FACTOR: EXACT; RELATIVE KERNEL OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
