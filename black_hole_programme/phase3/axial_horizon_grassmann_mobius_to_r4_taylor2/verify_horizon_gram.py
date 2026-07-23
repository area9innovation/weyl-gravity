#!/usr/bin/env python3
"""Independent exact verifier for the future-horizon outward Gram."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "future_horizon_outward_gram.json"
FACTOR_CERTIFICATE = HERE / "future_horizon_factor_quotient.json"


def parse_matrix(document: dict, omega: sp.Symbol) -> sp.Matrix:
    local = {"omega": omega, "I": sp.I}
    return sp.Matrix([
        [sp.sympify(value, locals=local) for value in row]
        for row in document["gram_without_pi_alpha_W"]
    ])


def conjugate(value: sp.Expr, omega: sp.Symbol) -> sp.Expr:
    return sp.conjugate(value).subs(sp.conjugate(omega), omega)


def strict_sign_on_interval(
    expression: sp.Expr,
    omega: sp.Symbol,
    expected: int,
) -> bool:
    expression = sp.cancel(expression)
    if sp.cancel(expression - conjugate(expression, omega)) != 0:
        return False
    numerator, denominator = sp.fraction(expression)
    lo, hi = sp.Rational(1, 2), sp.Rational(3, 4)
    for polynomial in (numerator, denominator):
        poly = sp.Poly(polynomial, omega)
        if poly.count_roots(lo, hi) != 0:
            return False
    value = sp.sign(sp.cancel(expression.subs(omega, lo)))
    return value == expected


def verify_document(document: dict) -> list[str]:
    errors: list[str] = []
    omega = sp.Symbol("omega", real=True)
    gram = parse_matrix(document, omega)
    if any(sp.cancel(gram[i, j] - conjugate(gram[j, i], omega)) != 0
           for i in range(3) for j in range(3)):
        errors.append("Gram is not Hermitian")
    minors = [sp.factor(gram[:size, :size].det())
              for size in range(1, 4)]
    recorded_minors = [
        sp.sympify(value, locals={"omega": omega, "I": sp.I})
        for value in document["leading_principal_minors"]
    ]
    if any(sp.cancel(left - right) != 0
           for left, right in zip(minors, recorded_minors)):
        errors.append("leading principal minor mismatch")
    pivots = [
        minors[0],
        sp.cancel(minors[1] / minors[0]),
        sp.cancel(minors[2] / minors[1]),
    ]
    recorded_pivots = [
        sp.sympify(value, locals={"omega": omega, "I": sp.I})
        for value in document["ldl_pivots"]
    ]
    if any(sp.cancel(left - right) != 0
           for left, right in zip(pivots, recorded_pivots)):
        errors.append("LDL pivot mismatch")
    signs = [1, -1, -1]
    if not all(strict_sign_on_interval(value, omega, sign)
               for value, sign in zip(pivots, signs)):
        errors.append("LDL interval sign proof failed")
    if document["inertia_for_alpha_W_positive"] != [1, 2, 0]:
        errors.append("inertia record mismatch")
    if document["rank"] != 3:
        errors.append("rank record mismatch")
    orientation = document["orientation"]
    if orientation != {
        "coordinate_radial": "K4=+I*Jhat",
        "future_horizon_outward": (
            "H_out=-Hframe^dagger*K4*Hframe"
            "=-I*Hframe^dagger*Jhat*Hframe"
        ),
    }:
        errors.append("future-horizon Stokes sign mismatch")
    disposition = document["semidefinite_disposition"]
    if (disposition["H_out_positive_semidefinite"]
            or disposition["minus_H_out_positive_semidefinite"]):
        errors.append("indefinite form mislabeled semidefinite")
    shortcut = document["stokes_rank_shortcut"]
    if shortcut["activated"] or shortcut["direct_endpoint_rank_bound"] is not None:
        errors.append("semidefinite Stokes shortcut was unsoundly activated")
    if document["order_three_sufficiency"][
        "minimum_omitted/exact_cross_current_order"
    ] != 2:
        errors.append("omitted-head power-count drift")
    if document["epsilon_method"]["status"] != "METHOD_SHORTFALL":
        errors.append("failed epsilon method was promoted")
    provenance = document["provenance"]
    literal = ROOT / provenance["literal_current"]
    if hashlib.sha256(literal.read_bytes()).hexdigest() != (
        provenance["literal_current_sha256"]
    ):
        errors.append("literal-current provenance hash drift")
    return errors


def verify_factor_document(document: dict) -> list[str]:
    errors: list[str] = []
    omega = sp.Symbol("omega", real=True)
    local = {"omega": omega, "I": sp.I}
    spin_two = document["spin_two_extension"]
    determinant = sp.sympify(spin_two["determinant"], locals=local)
    expected_determinant = (
        -sp.Rational(5184, 25) * omega ** 4
        * (16 * omega ** 2 + 1) ** 2 / (omega ** 2 + 1) ** 2
    )
    if sp.cancel(determinant - expected_determinant) != 0:
        errors.append("spin-two determinant mismatch")
    if not strict_sign_on_interval(determinant, omega, -1):
        errors.append("spin-two hyperbolic sign proof failed")
    quotient = document["spin_one_quotient"]
    unit = sp.sympify(quotient["unit_quotient_norm"], locals=local)
    if sp.cancel(unit + sp.Rational(32, 15) / omega) != 0:
        errors.append("unit spin-one quotient norm mismatch")
    if not strict_sign_on_interval(unit, omega, -1):
        errors.append("unit spin-one quotient sign proof failed")
    if (spin_two["inertia_for_alpha_W_positive"] != [1, 1, 0]
            or quotient["inertia_for_alpha_W_positive"] != [0, 1, 0]
            or document["full_inertia_for_alpha_W_positive"] != [1, 2, 0]):
        errors.append("factor inertia additivity mismatch")
    for prefix in ("gram", "devissage"):
        path = ROOT / document["provenance"][f"{prefix}_path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != (
            document["provenance"][f"{prefix}_sha256"]
        ):
            errors.append(f"{prefix} provenance hash drift")
    return errors


def verify() -> list[str]:
    return (
        verify_document(json.loads(CERTIFICATE.read_text()))
        + verify_factor_document(json.loads(FACTOR_CERTIFICATE.read_text()))
    )


if __name__ == "__main__":
    found = verify()
    if found:
        for error in found:
            print(f"FAIL {error}")
        raise SystemExit(1)
    print("verified=true inertia=1,2,0 semidefinite_shortcut=false")
