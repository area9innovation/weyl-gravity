#!/usr/bin/env python3
"""Independent exact replay of the scalar-triangle differential system."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
import sympy as sp


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "certificates/GENERIC_SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM.json"
SCHEMA = HERE / "schema/generic-scalar-triangle-differential-system-v1.schema.json"

X1, X2, X3 = sp.symbols("x1 x2 x3", positive=True)
XS = (X1, X2, X3)
J = sp.symbols("J_triangle")
LAMBDA = X1**2 + X2**2 + X3**2 - 2 * X1 * X2 - 2 * X1 * X3 - 2 * X2 * X3


def _q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _poly(terms: list[dict[str, Any]]) -> sp.Expr:
    return sp.expand(
        sum(
            _q(term["coefficient"])
            * X1 ** term["exponents"][0]
            * X2 ** term["exponents"][1]
            * X3 ** term["exponents"][2]
            for term in terms
        )
    )


def _rf(value: dict[str, Any]) -> sp.Expr:
    return sp.cancel(_poly(value["numerator_terms"]) / _poly(value["denominator_terms"]))


def _logs(expression: sp.Expr) -> sp.Expr:
    return sp.factor(sp.expand_log(sp.cancel(expression), force=True))


def _expected_derivatives() -> tuple[sp.Expr, sp.Expr, sp.Expr]:
    result = []
    for i in range(3):
        xi, xj, xk = XS[i], XS[(i + 1) % 3], XS[(i + 2) % 3]
        result.append(
            sp.cancel(
                (
                    (xj + xk - xi) * J
                    - (xi + xj - xk) * sp.log(xj / xi) / xi
                    - (xi + xk - xj) * sp.log(xk / xi) / xi
                )
                / LAMBDA
            )
        )
    return tuple(result)


def _angular_moment_from_partial_fractions(numerator: sp.Expr) -> sp.Expr:
    """Derive the angular moment after t=tan(theta), without using producer code."""
    t, a, b = sp.symbols("t a b", positive=True)
    A, B, C, D = sp.symbols("A B C D")
    identity = sp.Poly(
        (A * t + B) * (a + b * t) ** 2
        + C * (1 + t**2) * (a + b * t)
        + D * (1 + t**2)
        - numerator,
        t,
    )
    solution = sp.solve(identity.all_coeffs(), (A, B, C, D), dict=True)[0]
    antiderivative = (
        solution[A] * sp.log(1 + t**2) / 2
        + solution[B] * sp.atan(t)
        + solution[C] * sp.log(a + b * t) / b
        - solution[D] / (b * (a + b * t))
    )
    return sp.factor(sp.simplify(sp.limit(antiderivative, t, sp.oo) - antiderivative.subs(t, 0)))


def verify() -> None:
    stored = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(stored)
    locals_ = {"x1": X1, "x2": X2, "x3": X3, "J_triangle": J, "log": sp.log}
    rows = tuple(sp.sympify(row["formula"], locals=locals_) for row in stored["derivative_rows"])
    expected = _expected_derivatives()
    for i, (actual, reference) in enumerate(zip(rows, expected), start=1):
        if _logs(actual - reference) != 0:
            raise ValueError(f"stored triangle derivative drifted: x{i}")

    if _logs(sum(x * row for x, row in zip(XS, rows)) + J) != 0:
        raise ValueError("independent Euler identity failed")
    for i, j in ((0, 1), (0, 2), (1, 2)):
        left = sp.diff(rows[j], XS[i]) + sp.diff(rows[j], J) * rows[i]
        right = sp.diff(rows[i], XS[j]) + sp.diff(rows[i], J) * rows[j]
        if _logs(left - right) != 0:
            raise ValueError(f"independent mixed derivative failed: {i},{j}")

    expected_masters = {
        "M_x1": {
            "J_triangle": (X1 - X2 - X3) / LAMBDA,
            "log_x2_over_x1": (X1 + X2 - X3) / (X1 * LAMBDA),
            "log_x3_over_x1": (X1 + X3 - X2) / (X1 * LAMBDA),
        },
        "M_x2": {
            "J_triangle": (-X1 + X2 - X3) / LAMBDA,
            "log_x2_over_x1": -2 / LAMBDA,
            "log_x3_over_x1": (-X1 + X2 + X3) / (X2 * LAMBDA),
        },
    }
    for master_id, basis in expected_masters.items():
        for basis_id, reference in basis.items():
            if sp.cancel(_rf(stored["master_rows"][master_id][basis_id]) - reference) != 0:
                raise ValueError(f"master coefficient drifted: {master_id}/{basis_id}")

    a, b = sp.symbols("a b", positive=True)
    angular_locals = {"a": a, "b": b, "log": sp.log, "pi": sp.pi}
    i_cc = sp.sympify(stored["corner_angular_system"]["I_cos2"], locals=angular_locals)
    i_ss = sp.sympify(stored["corner_angular_system"]["I_sin2"], locals=angular_locals)
    expected_cc = _angular_moment_from_partial_fractions(sp.S.One)
    expected_ss = _angular_moment_from_partial_fractions(sp.symbols("t", positive=True) ** 2)
    # The helper owns its symbols; align them by name before comparing.
    expected_cc = expected_cc.subs({symbol: {"a": a, "b": b}[symbol.name] for symbol in expected_cc.free_symbols})
    expected_ss = expected_ss.subs({symbol: {"a": a, "b": b}[symbol.name] for symbol in expected_ss.free_symbols})
    if sp.simplify(i_cc - expected_cc) != 0:
        raise ValueError("independent cosine angular moment failed")
    if sp.simplify(i_ss - expected_ss) != 0:
        raise ValueError("independent sine angular moment failed")
    if sp.simplify(i_cc + i_ss - 1 / (a * b)) != 0:
        raise ValueError("independent corner angular sum failed")
    if i_cc.subs({a: 1, b: 1}) != sp.Rational(1, 2):
        raise ValueError("cosine angular normalization drifted")
    if i_ss.subs({a: 1, b: 1}) != sp.Rational(1, 2):
        raise ValueError("sine angular normalization drifted")

    payload = {
        key: stored[key]
        for key in ("derivative_rows", "master_rows", "identity_ledger", "corner_angular_system")
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if digest != stored["formula_digest"]:
        raise ValueError("scalar-triangle formula digest drifted")
    flags = stored["claim_flags"]
    if not all(
        flags[name]
        for name in (
            "SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED",
            "S3_COVARIANCE_VERIFIED",
            "HOMOGENEITY_VERIFIED",
            "MIXED_DERIVATIVE_INTEGRABILITY_VERIFIED",
            "TWO_LOG_MASTER_REDUCTION_COMPUTED",
            "EQUAL_WEIGHT_CORNER_ANGULAR_SUM_COMPUTED",
        )
    ):
        raise ValueError("positive scalar-triangle claim drifted")
    if any(
        flags[name]
        for name in (
            "GHOST_CHANNEL_FUNCTIONS_COMPUTED",
            "I29_POLE4_REDUCED",
            "COMPLETE_RENORMALIZED_GAMMA1_SUPPLIED",
            "COMPLETE_RENORMALIZED_Q1_SUPPLIED",
            "LORENTZIAN_CERTIFIED",
        )
    ):
        raise ValueError("scalar-triangle claim boundary drifted")


def main() -> int:
    verify()
    print("independent generic scalar-triangle differential system: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
