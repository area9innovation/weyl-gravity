#!/usr/bin/env python3
"""Independent replay of the integrated ghost vector n=1+n=2 functions."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from scipy.integrate import dblquad
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N1_N2_VECTOR_INTEGRATED_FUNCTIONS.json"
SCHEMA = HERE / "schema/generic-background-ghost-n1-n2-vector-integrated-functions-v1.schema.json"
A, B = sp.symbols("alpha1 alpha2")
X1, X2, X3 = sp.symbols("x1 x2 x3")
XS = (X1, X2, X3)
J, U, V = sp.symbols("J_triangle log_x2_over_x1 log_x3_over_x1")
DELTA = sp.expand((1 - A - B) * A * X2 + (1 - A - B) * B * X1 + A * B * X3)
BASIS = ("J_triangle", "log_x2_over_x1", "log_x3_over_x1", "rational_corner")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _from_q(value: dict[str, int]) -> sp.Rational:
    return sp.Rational(value["numerator"], value["denominator"])


def _rational(data: dict[str, Any]) -> sp.Expr:
    def polynomial(terms: list[dict[str, Any]]) -> sp.Expr:
        return sum(
            _from_q(term["coefficient"])
            * sp.prod(variable**power for variable, power in zip(XS, term["exponents"]))
            for term in terms
        )

    return sp.cancel(polynomial(data["numerator_terms"]) / polynomial(data["denominator_terms"]))


def _moments() -> dict[tuple[int, int], sp.Expr]:
    c = X3 - X1 - X2
    matrix = sp.Matrix(
        [
            [-2 * X2, c, 0, 0, 0],
            [c, -2 * X1, 0, 0, 0],
            [0, X2, 0, -2 * X2, c],
            [X1, 0, c, -2 * X1, 0],
            [X2, X1, -X2, c, -X1],
        ]
    )
    rhs = sp.Matrix(
        [
            V - X2 * J,
            V - U - X1 * J,
            V / 2,
            (V - U) / 2,
            sp.Rational(1, 2),
        ]
    )
    solution = matrix.inv() * rhs
    return {
        (0, 0): J,
        (1, 0): sp.cancel(solution[0]),
        (0, 1): sp.cancel(solution[1]),
        (2, 0): sp.cancel(solution[2]),
        (1, 1): sp.cancel(solution[3]),
        (0, 2): sp.cancel(solution[4]),
    }


def _parse(value: str) -> sp.Expr:
    return sp.sympify(
        value,
        locals={"alpha1": A, "alpha2": B, "x1": X1, "x2": X2, "x3": X3},
    )


def _direct_quadrature(expression: sp.Expr, point: tuple[float, float, float]) -> float:
    function = sp.lambdify((A, B, X1, X2, X3), expression, "numpy")
    value, _ = dblquad(
        lambda beta, alpha: function(alpha, beta, *point),
        0.0,
        1.0,
        lambda alpha: 0.0,
        lambda alpha: 1.0 - alpha,
        epsabs=2e-10,
        epsrel=2e-10,
    )
    return float(value)


def main() -> int:
    value = json.loads(CERTIFICATE.read_text())
    schema = json.loads(SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(value)
    dependencies = {}
    for name, reference in value["dependencies"].items():
        path = ROOT / reference["path"]
        if _sha256(path) != reference["sha256"]:
            raise ValueError(f"dependency hash drifted: {name}")
        dependency = json.loads(path.read_text())
        if dependency["result_id"] != reference["result_id"]:
            raise ValueError(f"dependency result id drifted: {name}")
        dependencies[name] = dependency

    source_rows = {
        f"{row['carrier_id']}_{''.join(str(item) for item in row['labels'])}": row
        for row in dependencies["vector_CPT_projection"]["vector_n1_plus_n2_channel_integrands"]
    }
    moments = _moments()
    stored_moments = {
        (int(key[2]), int(key[3])): sp.sympify(
            expression,
            locals={
                "x1": X1,
                "x2": X2,
                "x3": X3,
                "J_triangle": J,
                "log_x2_over_x1": U,
                "log_x3_over_x1": V,
            },
        )
        for key, expression in value["moment_rows"].items()
    }
    if any(sp.cancel(stored_moments[key] - moments[key]) != 0 for key in moments):
        raise ValueError("independent simplex moments drifted")

    reconstructed: dict[str, dict[str, sp.Expr]] = {}
    for row in value["channel_rows"]:
        channel_id = row["channel_id"]
        source = source_rows[channel_id]
        if row["source_integrand_digest"] != _digest(source):
            raise ValueError(f"source integrand digest drifted: {channel_id}")
        integrand = _parse(source["alpha_integrand"])
        numerator = sp.cancel(integrand * DELTA)
        polynomial = sp.Poly(numerator, A, B, domain="EX")
        integrated = sp.cancel(
            sum(coefficient * moments[powers] for powers, coefficient in polynomial.terms())
        )
        coordinates = {
            basis_id: _rational(row["function_basis_coordinates"][basis_id])
            for basis_id in BASIS
        }
        stored = sp.cancel(
            coordinates["J_triangle"] * J
            + coordinates["log_x2_over_x1"] * U
            + coordinates["log_x3_over_x1"] * V
            + coordinates["rational_corner"]
        )
        if sp.cancel(stored - integrated) != 0:
            raise ValueError(f"integrated vector function drifted: {channel_id}")
        reconstructed[channel_id] = coordinates

    i28_ids = ("I28_123", "I28_132", "I28_231")
    if any(
        sp.cancel(sum(reconstructed[channel][basis_id] for channel in i28_ids)) != 0
        for basis_id in BASIS
    ):
        raise ValueError("independent I28 relation failed")

    point = (2.0, 3.0, 5.0)
    j_value = _direct_quadrature(1 / DELTA, point)
    logs = (sp.log(sp.Rational(3, 2)), sp.log(sp.Rational(5, 2)))
    for channel_id, source in source_rows.items():
        if source["identically_zero"]:
            continue
        coordinates = reconstructed[channel_id]
        substitution = dict(zip(XS, map(sp.Rational, (2, 3, 5))))
        predicted = float(
            sp.N(
                coordinates["J_triangle"].subs(substitution) * j_value
                + coordinates["log_x2_over_x1"].subs(substitution) * logs[0]
                + coordinates["log_x3_over_x1"].subs(substitution) * logs[1]
                + coordinates["rational_corner"].subs(substitution),
                17,
            )
        )
        direct = _direct_quadrature(_parse(source["alpha_integrand"]), point)
        if abs(predicted - direct) > 2e-8:
            raise ValueError(f"direct quadrature drifted: {channel_id}")

    payload = {
        "moment_rows": value["moment_rows"],
        "channel_rows": value["channel_rows"],
        "identity_ledger": value["identity_ledger"],
    }
    if _digest(payload) != value["formula_digest"]:
        raise ValueError("formula digest drifted")
    print("GENERIC GHOST VECTOR N1+N2 INTEGRATED FUNCTIONS CONSUMER: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
