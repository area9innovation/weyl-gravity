#!/usr/bin/env python3
"""Certify the massless scalar-triangle differential and corner systems."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json"
SCHEMA = HERE / "schema/generic-scalar-triangle-differential-system-v1.schema.json"

X1, X2, X3 = sp.symbols("x1 x2 x3", positive=True)
XS = (X1, X2, X3)
J = sp.symbols("J_triangle")
L21 = sp.log(X2 / X1)
L31 = sp.log(X3 / X1)
LAMBDA = sp.expand(
    X1**2 + X2**2 + X3**2 - 2 * X1 * X2 - 2 * X1 * X3 - 2 * X2 * X3
)


def _q(value: sp.Expr | int) -> dict[str, int]:
    value = sp.Rational(value)
    return {"numerator": int(value.p), "denominator": int(value.q)}


def _poly_terms(expression: sp.Expr) -> list[dict[str, Any]]:
    polynomial = sp.Poly(sp.expand(expression), *XS, domain=sp.QQ)
    return [
        {"exponents": list(exponents), "coefficient": _q(coefficient)}
        for exponents, coefficient in polynomial.terms()
        if coefficient
    ]


def _rational_function(expression: sp.Expr) -> dict[str, Any]:
    numerator, denominator = sp.fraction(sp.cancel(expression))
    numerator = sp.Poly(numerator, *XS, domain=sp.QQ)
    denominator = sp.Poly(denominator, *XS, domain=sp.QQ)
    if denominator.LC() < 0:
        numerator = -numerator
        denominator = -denominator
    return {
        "numerator_terms": _poly_terms(numerator.as_expr()),
        "denominator_terms": _poly_terms(denominator.as_expr()),
    }


def derivative_rows() -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    rows = []
    for index in range(3):
        xi = XS[index]
        xj = XS[(index + 1) % 3]
        xk = XS[(index + 2) % 3]
        rows.append(
            sp.cancel(
                (
                    (xj + xk - xi) * J
                    - (xi + xj - xk) * sp.log(xj / xi) / xi
                    - (xi + xk - xj) * sp.log(xk / xi) / xi
                )
                / LAMBDA
            )
        )
    return tuple(rows)


def _expanded_logs(expression: sp.Expr) -> sp.Expr:
    return sp.factor(sp.expand_log(sp.cancel(expression), force=True))


def _total_derivative(expression: sp.Expr, variable: sp.Symbol, row: sp.Expr) -> sp.Expr:
    return _expanded_logs(sp.diff(expression, variable) + sp.diff(expression, J) * row)


def master_rows() -> dict[str, dict[str, sp.Expr]]:
    d1, d2, _ = derivative_rows()
    rows = {}
    for master_id, expression in (("M_x1", -d1), ("M_x2", -d2)):
        expanded = sp.expand_log(expression, force=True).expand()
        j_coefficient = sp.cancel(expanded.coeff(J))
        remainder = sp.cancel(expanded - j_coefficient * J)
        # Work in the two independent logarithms log(x2/x1), log(x3/x1).
        u, v = sp.symbols("u v")
        formal = sp.expand(
            remainder.xreplace(
                {
                    sp.log(X1): 0,
                    sp.log(X2): u,
                    sp.log(X3): v,
                }
            )
        )
        l21_coefficient = sp.cancel(formal.coeff(u))
        l31_coefficient = sp.cancel(formal.coeff(v))
        if sp.cancel(formal - l21_coefficient * u - l31_coefficient * v) != 0:
            raise ValueError(f"logarithm-basis reduction failed: {master_id}")
        rows[master_id] = {
            "J_triangle": j_coefficient,
            "log_x2_over_x1": l21_coefficient,
            "log_x3_over_x1": l31_coefficient,
        }
    return rows


def angular_rows() -> dict[str, sp.Expr]:
    a, b = sp.symbols("a b", positive=True)
    common = (a**2 + b**2) ** 2
    i_cc = sp.cancel(
        (
            sp.pi * a**3
            - 4 * a**2 * b * sp.log(a)
            + 4 * a**2 * b * sp.log(b)
            + 2 * a**2 * b
            - sp.pi * a * b**2
            + 2 * b**3
        )
        / (2 * a * common)
    )
    i_ss = sp.cancel(
        (
            2 * a**3
            - sp.pi * a**2 * b
            + 4 * a * b**2 * sp.log(a)
            - 4 * a * b**2 * sp.log(b)
            + 2 * a * b**2
            + sp.pi * b**3
        )
        / (2 * b * common)
    )
    if sp.simplify(i_cc + i_ss - 1 / (a * b)) != 0:
        raise ValueError("corner angular sum identity failed")
    return {"I_cos2": i_cc, "I_sin2": i_ss, "equal_weight_sum": 1 / (a * b)}


def _formula_payload() -> dict[str, Any]:
    derivatives = derivative_rows()
    masters = master_rows()

    homogeneity = _expanded_logs(sum(x * row for x, row in zip(XS, derivatives)) + J)
    if homogeneity != 0:
        raise ValueError("triangle homogeneity identity failed")

    integrability = []
    for i, j in ((0, 1), (0, 2), (1, 2)):
        defect = _expanded_logs(
            _total_derivative(derivatives[j], XS[i], derivatives[i])
            - _total_derivative(derivatives[i], XS[j], derivatives[j])
        )
        if defect != 0:
            raise ValueError(f"triangle integrability failed: {i + 1},{j + 1}")
        integrability.append({"pair": [i + 1, j + 1], "defect": "ZERO"})

    covariance = []
    for permutation in (
        (0, 1, 2),
        (0, 2, 1),
        (1, 0, 2),
        (1, 2, 0),
        (2, 0, 1),
        (2, 1, 0),
    ):
        substitution = {XS[i]: XS[permutation[i]] for i in range(3)}
        for i in range(3):
            transformed = derivatives[i].subs(substitution, simultaneous=True)
            defect = _expanded_logs(transformed - derivatives[permutation[i]])
            if defect != 0:
                raise ValueError(f"triangle S3 covariance failed: {permutation},{i}")
        covariance.append({"permutation": list(permutation), "defect": "ZERO"})

    symmetric = [
        sp.simplify(row.subs({X1: 1, X2: 1, X3: 1})) for row in derivatives
    ]
    if symmetric != [-J / 3] * 3:
        raise ValueError("symmetric-point derivative normalization failed")

    return {
        "derivative_rows": [
            {
                "variable": f"x{index + 1}",
                "formula": sp.sstr(row),
            }
            for index, row in enumerate(derivatives)
        ],
        "master_rows": {
            master_id: {
                basis_id: _rational_function(coefficient)
                for basis_id, coefficient in row.items()
            }
            for master_id, row in masters.items()
        },
        "identity_ledger": {
            "euler_homogeneity": "x1*d1J+x2*d2J+x3*d3J=-J",
            "euler_defect": "ZERO",
            "mixed_integrability": integrability,
            "S3_covariance": covariance,
            "symmetric_point_derivatives": ["-J_triangle/3"] * 3,
        },
        "corner_angular_system": {
            "I_cos2": sp.sstr(angular_rows()["I_cos2"]),
            "I_sin2": sp.sstr(angular_rows()["I_sin2"]),
            "equal_weight_sum": "1/(a*b)",
            "equal_weight_sum_defect": "ZERO",
        },
    }


def build() -> dict[str, Any]:
    payload = _formula_payload()
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    result = {
        "schema": "quantum-weyl-generic-scalar-triangle-differential-system-v1",
        "result_id": "GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM",
        "result_state": "COEFFICIENT_COMPUTED",
        "lifecycle_state": "SCALAR_TRIANGLE_DERIVATIVES_AND_CORNER_ANGULAR_SYSTEM_CERTIFIED",
        "dependency_tags": ["EUCLIDEAN-SPECTRAL"],
        "scope": {
            "dimension": 4,
            "signature": "Euclidean",
            "kinematics": "positive nonexceptional x1,x2,x3 with Kallen lambda nonzero",
            "integral": "J_triangle=integral_simplex 1/Delta",
        },
        "convention": {
            "Kallen_lambda": "x1^2+x2^2+x3^2-2*x1*x2-2*x1*x3-2*x2*x3",
            "log_basis": ["log(x2/x1)", "log(x3/x1)"],
            "derivative_masters": ["M_x1=-dJ_triangle/dx1", "M_x2=-dJ_triangle/dx2"],
        },
        **payload,
        "formula_digest": digest,
        "provenance": {
            "primary_source": {
                "authors": "Barak Kol and Subhajit Mazumdar",
                "title": "Triangle diagram, Distance Geometry and Symmetries of Feynman Integrals",
                "arxiv": "1909.04055",
                "url": "https://arxiv.org/abs/1909.04055",
                "role": "differential-system architecture and bubble descendants; every stored identity is independently replayed",
            }
        },
        "claim_flags": {
            "SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED": True,
            "S3_COVARIANCE_VERIFIED": True,
            "HOMOGENEITY_VERIFIED": True,
            "MIXED_DERIVATIVE_INTEGRABILITY_VERIFIED": True,
            "TWO_LOG_MASTER_REDUCTION_COMPUTED": True,
            "EQUAL_WEIGHT_CORNER_ANGULAR_SUM_COMPUTED": True,
            "GHOST_CHANNEL_FUNCTIONS_COMPUTED": False,
            "I29_POLE4_REDUCED": False,
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED": False,
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED": False,
            "LORENTZIAN_CERTIFIED": False,
        },
        "next_gate": "COMBINE_WITH_THE_TEN_POLE3_RELATIVE_IBP_ROWS_AND_THEIR_PUNCTURED_CORNER_FLUXES",
        "claim_boundary": (
            "This EUCLIDEAN-SPECTRAL certificate gives the exact two-log differential system for the positive nonexceptional massless scalar triangle and the exact corner angular moments needed by the pole-three relative-IBP rows. It does not by itself integrate a ghost channel, reduce the pole-four I29 row, supply the physical fourth-order Hessian, complete Gamma1/Q1, authorize residual transfer, or establish a Lorentzian, Hadamard, particle, positivity, scattering, or unitarity claim."
        ),
    }
    validate(result)
    return result


def validate(value: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    payload = {
        key: value[key]
        for key in (
            "derivative_rows",
            "master_rows",
            "identity_ledger",
            "corner_angular_system",
        )
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != value["formula_digest"]:
        raise ValueError("scalar-triangle differential formula digest drifted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = json.dumps(build(), indent=2, sort_keys=True) + "\n"
    if args.emit:
        OUTPUT.write_text(rendered)
    if args.check and (not OUTPUT.exists() or OUTPUT.read_text() != rendered):
        raise SystemExit(f"stale scalar-triangle differential certificate: {OUTPUT}")
    if not args.emit and not args.check:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
