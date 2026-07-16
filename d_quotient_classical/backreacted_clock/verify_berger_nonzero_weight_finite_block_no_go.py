#!/usr/bin/env python3
"""Independent exact audit of the Berger finite nonzero-weight closure no-go."""

from __future__ import annotations

import json
from pathlib import Path

import sympy as sp


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO.json"


def _expression(raw: str, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    return sp.sympify(raw, locals={str(variable): variable for variable in variables})


def verify_certificate() -> dict[str, object]:
    payload = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    u, lapse, rho, omega = sp.symbols("u N rho omega", real=True)
    q0 = sp.Rational(9, 40)
    c0 = sp.sqrt(q0)
    c = c0 * (1 + u)
    lagrangian = sp.factor(lapse * c * (
        sp.Rational(5, 8) * 4 * (1 - c**2) ** 2 / 3
        + rho**2 * omega**2 / (2 * lapse**2)
        - (4 - c**2) * rho**2 / 24
        - sp.Rational(119, 1920) * rho**4
    ) / c0)
    fields = (u, lapse, rho)
    fixture = {u: 0, lapse: 1, rho: 1, omega: sp.Rational(3, 4)}
    assert all(sp.factor(sp.diff(lagrangian, field).subs(fixture)) == 0 for field in fields)

    x = sp.symbols("x_u x_N x_rho", real=True)
    square_map = []
    for output in range(3):
        value = sum(
            sp.diff(lagrangian, fields[output], fields[left], fields[right]).subs(fixture)
            * x[left] * x[right]
            for left in range(3)
            for right in range(3)
        )
        square_map.append(sp.factor(value))
    observed = [_expression(value, x) for value in payload["square_map"]["components"]]
    assert all(sp.expand(left - right) == 0 for left, right in zip(square_map, observed))

    real = payload["real_anisotropy_certificate"]
    combination = sum(sp.Rational(coefficient) * square_map[index] for index, coefficient in enumerate(real["combination_coefficients"]))
    gram = sp.Matrix([[sp.Rational(value) for value in row] for row in real["gram_matrix"]])
    assert sp.expand((sp.Matrix(x).T * gram * sp.Matrix(x))[0] - combination) == 0
    minors = [sp.factor(gram[:size, :size].det()) for size in range(1, 4)]
    assert minors == [sp.Rational(value) for value in real["leading_principal_minors"]]
    assert all(value > 0 for value in minors)

    complex_certificate = payload["complex_anisotropy_certificate"]
    targets = [_expression(value, x) for value in complex_certificate["targets"]]
    for target, raw_multipliers in zip(targets, complex_certificate["multipliers_by_target"]):
        multipliers = [_expression(value, x) for value in raw_multipliers]
        assert sp.expand(sum(multiplier * generator for multiplier, generator in zip(multipliers, square_map)) - target) == 0
    assert sp.expand(targets[0] - x[2] ** 4) == 0
    assert sp.expand(targets[1].subs(x[2], 0) - x[0] ** 2) == 0
    assert sp.expand(targets[2].subs(x[2], 0) - x[1] ** 2) == 0

    leakage = [sp.factor(value.subs({x[0]: 1, x[1]: 0, x[2]: 0})) for value in square_map]
    failed = payload["first_failed_block"]
    assert leakage == [sp.Rational(value) for value in failed["leakage_vector"]]
    witness = [sp.Rational(value) for value in failed["normalized_dual_witness"]]
    assert sum(left * right for left, right in zip(leakage, witness)) == 1
    weights = payload["finite_block_no_go"]["sample_forced_weights"]
    assert all(weights[index + 1] == -2 * weights[index] for index in range(len(weights) - 1))

    assert payload["flags"]["BERGER_NONZERO_WEIGHT_FINITE_BLOCK_NO_GO"] is True
    assert payload["flags"]["NONZERO_WEIGHT_MODE_CLOSURE_OBSTRUCTION"] is True
    assert payload["flags"]["NONZERO_WEIGHT_D_CARTAN_OBSTRUCTION"] is False
    assert payload["flags"]["CLASSICAL_SUPPORT_LOCAL_Q2"] is False
    return payload


def main() -> None:
    verify_certificate()
    print("BERGER_NONZERO_D_WEIGHT_FINITE_BLOCK_NO_GO_INDEPENDENT: PASS")
    print("finite nonzero-weight cyclic q2-closed block: EXACTLY OBSTRUCTED")
    print("infinite all-weight and full support-local complexes: OPEN")


if __name__ == "__main__":
    main()
