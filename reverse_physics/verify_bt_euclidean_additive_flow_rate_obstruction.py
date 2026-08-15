#!/usr/bin/env python3
"""Independent symbolic verifier for the BT additive-flow rate obstruction."""

from __future__ import annotations

import ast
import hashlib
import json
import os
from fractions import Fraction

import jsonschema
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_FLOW_RATE_OBSTRUCTION_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-additive-flow-rate-obstruction-v1.schema.json"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_ADDITIVE_CONTRACTION_AXIAL_COERCIVITY_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_UNIQUE_CRITICAL_POINT_GRADIENT_GATE_V1.json",
]


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def enc(value: sp.Expr | Fraction | int) -> dict[str, int]:
    value = sp.cancel(value)
    return {"numerator": int(sp.numer(value)), "denominator": int(sp.denom(value))}


def direct_objects(x: sp.Expr) -> dict[str, sp.Expr | list[sp.Expr]]:
    omega = [x, x**-3, x**-3, x**-3, x, x**7]
    residual = [
        sp.cancel(omega[(i - 1) % 6] / omega[i] + omega[(i + 1) % 6] / omega[i] - 2)
        for i in range(6)
    ]
    derivative = sp.zeros(6)
    for i in range(6):
        for j in ((i - 1) % 6, (i + 1) % 6):
            derivative[i, j] += omega[j] / omega[i]
            derivative[i, i] -= omega[j] / omega[i]
    gradient = derivative.T * sp.Matrix(residual)
    residual_square = sp.factor(sum(value**2 for value in residual))
    action = residual_square / 2
    dissipation = sp.factor(sum(residual[i] ** 2 / omega[i] for i in range(6)))
    reciprocal_sum = sp.factor(sum(1 / value for value in omega))
    gradient_square = sp.factor(sum(value**2 for value in gradient))
    return {
        "omega": omega,
        "residual": residual,
        "residual_square": residual_square,
        "action": action,
        "dissipation": dissipation,
        "reciprocal_sum": reciprocal_sum,
        "gradient_square": gradient_square,
        "unnormalized_rate": sp.cancel(dissipation / action),
        "normalized_rate": sp.cancel(dissipation / (reciprocal_sum * action)),
        "gradient_quotient": sp.cancel(gradient_square / residual_square),
    }


def direct_row(m: int, symbolic: dict[str, sp.Expr | list[sp.Expr]]) -> dict:
    x_value = 2**m
    substitute = {X: x_value}
    get = lambda key: sp.cancel(symbolic[key].subs(substitute))  # type: ignore[union-attr]
    return {
        "m": m,
        "x": x_value,
        "exponents": [m, -3 * m, -3 * m, -3 * m, m, 7 * m],
        "geometric_mean_gauge_product": enc(1),
        "residual_square_per_axial_cycle": enc(get("residual_square")),
        "action_per_axial_cycle": enc(get("action")),
        "unnormalized_additive_dissipation": enc(get("dissipation")),
        "unnormalized_relative_action_decay": enc(get("unnormalized_rate")),
        "normalized_additive_dissipation": enc(get("dissipation") / get("reciprocal_sum")),
        "normalized_relative_action_decay": enc(get("normalized_rate")),
        "euclidean_action_gradient_square": enc(get("gradient_square")),
        "euclidean_gradient_quotient": enc(get("gradient_quotient")),
    }


X = sp.symbols("x", positive=True)


def main() -> int:
    with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
        certificate = json.load(handle)
    with open(os.path.join(ROOT, SCHEMA_REL), encoding="utf-8") as handle:
        schema = json.load(handle)
    jsonschema.Draft202012Validator(schema).validate(certificate)

    with open(__file__, encoding="utf-8") as handle:
        syntax = ast.parse(handle.read())
    imports = {
        alias.name
        for node in ast.walk(syntax)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "bt_euclidean_additive_flow_rate_obstruction" not in imports
    assert certificate["provenance"]["input_sha256"] == {
        relative: sha256(relative) for relative in INPUTS
    }

    symbolic = direct_objects(X)
    omega = symbolic["omega"]
    residual = symbolic["residual"]
    assert isinstance(omega, list) and isinstance(residual, list)
    assert sp.prod(omega) == 1
    expected_residual = [
        X**6 + X**-4 - 2,
        X**4 - 1,
        0,
        X**4 - 1,
        X**6 + X**-4 - 2,
        2 * X**-6 - 2,
    ]
    assert all(sp.cancel(actual - expected) == 0 for actual, expected in zip(residual, expected_residual))

    assert [direct_row(m, symbolic) for m in (1, 2, 4, 8)] == certificate["exact_rows"]

    assert sp.limit(X * symbolic["unnormalized_rate"], X, sp.oo) == 4
    assert sp.limit(X**4 * symbolic["normalized_rate"], X, sp.oo) == sp.Rational(4, 3)
    assert sp.limit(symbolic["gradient_quotient"] / X**12, X, sp.oo) == 3
    assert sp.limit(symbolic["unnormalized_rate"], X, sp.oo) == 0
    assert sp.limit(symbolic["normalized_rate"], X, sp.oo) == 0
    assert sp.limit(symbolic["gradient_quotient"], X, sp.oo) == sp.oo

    for key, expected in {
        "residual_square": (12, 2),
        "dissipation": (11, 4),
        "reciprocal_sum": (3, 3),
        "gradient_square": (24, 6),
    }.items():
        numerator, denominator = sp.fraction(sp.cancel(symbolic[key]))
        polynomial = sp.Poly(numerator, X)
        denominator_poly = sp.Poly(denominator, X)
        exponent = polynomial.degree() - denominator_poly.degree()
        coefficient = polynomial.LC() / denominator_poly.LC()
        cert_key = "additive_dissipation" if key == "dissipation" else key
        assert certificate["leading_laurent_terms"][cert_key] == {
            "exponent": exponent,
            "coefficient": enc(coefficient),
        }

    print(
        "[PASS] independent BT additive flow-rate verifier "
        "(schema, hashes, direct residual/Jacobian, exact rows, symbolic limits)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
