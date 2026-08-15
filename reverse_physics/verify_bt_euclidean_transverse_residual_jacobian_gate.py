#!/usr/bin/env python3
"""Independent SymPy verifier for the BT transverse-Jacobian gate."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import ast
from fractions import Fraction

import jsonschema
import sympy as sp


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_TRANSVERSE_RESIDUAL_JACOBIAN_GATE_V1.json"
)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-transverse-residual-jacobian-gate-v1.schema.json"
)
INPUTS = [
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1.json",
    "reverse_physics/certificates/REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_WEIGHTED_CURRENT_GATE_V2.json",
]
N = 6
BASIS = sp.Matrix(
    [
        [-1, -2, -2],
        [2, 3, 2],
        [-2, -2, -1],
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
    ]
)


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def enc(value: Fraction | int | sp.Rational) -> dict[str, int]:
    value = Fraction(int(sp.numer(value)), int(sp.denom(value)))
    return {"numerator": value.numerator, "denominator": value.denominator}


def derive_polynomial(projected: bool) -> dict[tuple[int, ...], Fraction]:
    omega = sp.symbols("omega0:6", positive=True)
    derivative = sp.zeros(N)
    for i in range(N):
        for j in ((i - 1) % N, (i + 1) % N):
            derivative[i, j] += omega[j] / omega[i]
            derivative[i, i] -= omega[j] / omega[i]
    if projected:
        derivative = (sp.eye(N) - sp.ones(N) / N) * derivative
    restricted = derivative * BASIS
    squared = sp.Rational(1, int((BASIS.T * BASIS).det())) * sum(
        (
            restricted.extract(rows, range(3)).det(method="domain-ge") ** 2
            for rows in itertools.combinations(range(N), 3)
        ),
        sp.Integer(0),
    )
    polynomial: dict[tuple[int, ...], Fraction] = {}
    for term in sp.Add.make_args(sp.expand(squared)):
        powers = term.as_powers_dict()
        exponent = tuple(int(powers.get(variable, 0)) for variable in omega)
        monomial = sp.prod(omega[i] ** exponent[i] for i in range(N))
        coefficient = sp.cancel(term / monomial)
        polynomial[exponent] = Fraction(int(sp.numer(coefficient)), int(sp.denom(coefficient)))
    return polynomial


def canonical_hash(polynomial: dict[tuple[int, ...], Fraction]) -> str:
    rows = []
    for exponent in sorted(polynomial):
        coefficient = polynomial[exponent]
        rows.append(
            ",".join(str(value) for value in exponent)
            + f":{coefficient.numerator}/{coefficient.denominator}\n"
        )
    return hashlib.sha256("".join(rows).encode("ascii")).hexdigest()


def stats(polynomial: dict[tuple[int, ...], Fraction]) -> dict:
    positive = [coefficient for coefficient in polynomial.values() if coefficient > 0]
    negative = [coefficient for coefficient in polynomial.values() if coefficient < 0]
    return {
        "term_count": len(polynomial),
        "positive_term_count": len(positive),
        "negative_term_count": len(negative),
        "positive_coefficient_sum": enc(sum(positive, Fraction())),
        "negative_coefficient_sum": enc(sum(negative, Fraction())),
        "vacuum_value": enc(sum(polynomial.values(), Fraction())),
        "coefficient_weighted_exponent_sum": [
            enc(
                sum(
                    (
                        coefficient * exponent[i]
                        for exponent, coefficient in polynomial.items()
                    ),
                    Fraction(),
                )
            )
            for i in range(N)
        ],
        "canonical_polynomial_sha256": canonical_hash(polynomial),
    }


def moment_hessian(
    polynomial: dict[tuple[int, ...], Fraction],
    point: tuple[int, ...],
) -> sp.Matrix:
    entries = [[Fraction() for _ in range(N)] for _ in range(N)]
    for exponent, coefficient in polynomial.items():
        power = sum(exponent[i] * point[i] for i in range(N))
        weight = coefficient * (
            Fraction(2**power) if power >= 0 else Fraction(1, 2 ** (-power))
        )
        for i in range(N):
            for j in range(N):
                entries[i][j] += weight * exponent[i] * exponent[j]
    return sp.Matrix(
        [[sp.Rational(value.numerator, value.denominator) for value in row] for row in entries]
    )


def evaluate(
    polynomial: dict[tuple[int, ...], Fraction], point: tuple[int, ...]
) -> Fraction:
    grouped: dict[int, Fraction] = {}
    for exponent, coefficient in polynomial.items():
        power = sum(exponent[i] * point[i] for i in range(N))
        grouped[power] = grouped.get(power, Fraction()) + coefficient
    return sum(
        (
            coefficient
            * (Fraction(2**power) if power >= 0 else Fraction(1, 2 ** (-power)))
            for power, coefficient in grouped.items()
        ),
        Fraction(),
    )


def dyadic_box(polynomial: dict[tuple[int, ...], Fraction]) -> tuple[int, Fraction, list[list[int]]]:
    minimum: Fraction | None = None
    minimizers: list[list[int]] = []
    count = 0
    for first in itertools.product(range(-3, 4), repeat=5):
        last = -sum(first)
        if not -3 <= last <= 3:
            continue
        point = first + (last,)
        value = evaluate(polynomial, point)
        count += 1
        if minimum is None or value < minimum:
            minimum = value
            minimizers = [list(point)]
        elif value == minimum:
            minimizers.append(list(point))
    assert minimum is not None
    return count, minimum, minimizers


def main() -> int:
    with open(os.path.join(ROOT, CERT_REL), encoding="utf-8") as handle:
        certificate = json.load(handle)
    with open(os.path.join(ROOT, SCHEMA_REL), encoding="utf-8") as handle:
        schema = json.load(handle)
    jsonschema.Draft202012Validator(schema).validate(certificate)

    with open(__file__, encoding="utf-8") as handle:
        verifier_source = handle.read()
    syntax = ast.parse(verifier_source)
    imported_modules = {
        alias.name
        for node in ast.walk(syntax)
        if isinstance(node, (ast.Import, ast.ImportFrom))
        for alias in node.names
    }
    assert "bt_euclidean_transverse_residual_jacobian_gate" not in imported_modules

    assert certificate["provenance"]["input_sha256"] == {
        relative: sha256(relative) for relative in INPUTS
    }

    unprojected = derive_polynomial(projected=False)
    projected = derive_polynomial(projected=True)
    assert stats(unprojected) == certificate["laurent_audit"]["unprojected_Dr"]
    assert stats(projected) == certificate["laurent_audit"]["centered_P_H_Dr"]

    vacuum_moment = moment_hessian(projected, (0, 0, 0, 0, 0, 0))
    vacuum_value = sum(projected.values(), Fraction())
    vacuum_log_jacobian = vacuum_moment / (2 * vacuum_value)
    assert [enc(vacuum_log_jacobian[0, j]) for j in range(N)] == certificate[
        "local_vacuum_result"
    ]["log_jacobian_hessian_first_row"]
    row = [vacuum_log_jacobian[0, j] for j in range(N)]
    a, b, c, d, c2, b2 = row
    assert b == b2 and c == c2
    eigenvalues = [
        a + 2 * b + 2 * c + d,
        a + b - c - d,
        a - b - c + d,
        a - 2 * b + 2 * c - d,
        a - b - c + d,
        a + b - c - d,
    ]
    assert [enc(value) for value in eigenvalues] == certificate[
        "local_vacuum_result"
    ]["fourier_eigenvalues"]

    point = tuple(certificate["exact_nonconvexity_witness"]["dyadic_log2_exponents"])
    nonconvex_hessian = moment_hessian(projected, point)
    minors = [sp.factor(nonconvex_hessian[:size, :size].det()) for size in range(1, N + 1)]
    assert [enc(value) for value in minors] == certificate[
        "exact_nonconvexity_witness"
    ]["squared_jacobian_log_field_hessian_leading_principal_minors"]
    assert minors[4] < 0

    count, minimum, minimizers = dyadic_box(projected)
    assert count == certificate["finite_search"]["point_count"]
    assert enc(minimum) == certificate["finite_search"]["minimum"]
    assert minimizers == certificate["finite_search"]["minimizers"]

    print(
        "[PASS] independent BT transverse residual-Jacobian verifier "
        "(schema, hashes, two Laurent expansions, Hessians, exact box)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
