#!/usr/bin/env python3
"""Independent Wick-pairing replay of the ghost n=3 angular carrier."""

from __future__ import annotations

from fractions import Fraction
import itertools
import json

import sympy as sp

from .generic_background_ghost_n3_adiabatic_carrier import DEPENDENCY, OUTPUT, build


def _f(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _pairings(items: tuple[int, ...]) -> list[tuple[tuple[int, int], ...]]:
    if not items:
        return [()]
    first = items[0]
    result = []
    for position in range(1, len(items)):
        second = items[position]
        rest = items[1:position] + items[position + 1 :]
        for tail in _pairings(rest):
            result.append(((first, second),) + tail)
    return result


def _sphere_moment(exponents: tuple[int, ...], dimension: int) -> Fraction:
    order = sum(exponents)
    if order % 2:
        return Fraction(0)
    labels = tuple(index for index, count in enumerate(exponents) for _ in range(count))
    pair_count = order // 2
    denominator = 1
    for shift in range(pair_count):
        denominator *= dimension + 2 * shift
    surviving = sum(
        all(left == right for left, right in pairing)
        for pairing in _pairings(labels)
    )
    return Fraction(surviving, denominator)


def verify() -> dict:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("three-insertion carrier is stale")
    parent = json.loads(DEPENDENCY.read_text())
    if parent["result_id"] != stored["dependency"]["result_id"]:
        raise ValueError("three-insertion parent drifted")

    # Independent diagonal-eigenvalue expansion.  Isotropy makes a diagonal
    # symmetric R sufficient to recover the three invariant coefficients.
    xs = sp.symbols("x0:4")
    d = 4
    a = sum(
        xs[i] * _sphere_moment(tuple(2 if j == i else 0 for j in range(d)), d)
        for i in range(d)
    )
    b = sum(
        xs[i] ** 2 * _sphere_moment(tuple(2 if j == i else 0 for j in range(d)), d)
        for i in range(d)
    )
    ab = sum(
        xs[i] * xs[j] ** 2
        * _sphere_moment(tuple(2 * ((k == i) + (k == j)) for k in range(d)), d)
        for i, j in itertools.product(range(d), repeat=2)
    )
    a3 = sum(
        xs[i] * xs[j] * xs[k]
        * _sphere_moment(
            tuple(2 * ((m == i) + (m == j) + (m == k)) for m in range(d)), d
        )
        for i, j, k in itertools.product(range(d), repeat=3)
    )
    tr1 = sum(xs)
    tr2 = sum(x**2 for x in xs)
    tr3 = sum(x**3 for x in xs)
    if sp.expand(a - tr1 / d) != 0 or sp.expand(b - tr2 / d) != 0:
        raise ValueError("second sphere moment replay failed")
    if sp.expand(ab - (tr1 * tr2 + 2 * tr3) / (d * (d + 2))) != 0:
        raise ValueError("fourth sphere moment replay failed")
    if sp.expand(
        a3 - (tr1**3 + 6 * tr1 * tr2 + 8 * tr3) / (d * (d + 2) * (d + 4))
    ) != 0:
        raise ValueError("sixth sphere moment replay failed")

    c = sp.Rational(1, 3)
    angular = sp.expand(tr3 - 3 * c * tr3 / d + 3 * c**2 * ab - c**3 * a3)
    expected = (
        sp.Rational(503, 648) * tr3
        + sp.Rational(11, 864) * tr1 * tr2
        - sp.Rational(1, 5184) * tr1**3
    )
    if sp.expand(angular - expected) != 0:
        raise ValueError("projector angular numerator replay failed")

    coefficients = stored["angular_average"]["coefficients"]
    if tuple(_f(coefficients[key]) for key in ("tr_R3", "tr_R_tr_R2", "tr_R_cubed")) != (
        Fraction(503, 648), Fraction(11, 864), Fraction(-1, 5184)
    ):
        raise ValueError("stored angular coefficients drifted")
    log = stored["three_insertion_log_term"]["coefficients"]
    if tuple(_f(log[key]) for key in ("tr_R3", "tr_R_tr_R2", "tr_R_cubed")) != (
        Fraction(-503, 243), Fraction(-11, 324), Fraction(1, 1944)
    ):
        raise ValueError("stored logarithm coefficients drifted")
    if stored["carrier_crosswalk"]["repository_I10_normalization_map"] != "NO_CERTIFIED_MAP":
        raise ValueError("three-insertion carrier crossed the I10 boundary")

    # Independent polarization check on three noncommuting symmetric matrices.
    r1 = sp.Matrix([[1, 2, 0, 0], [2, -1, 1, 0], [0, 1, 0, 1], [0, 0, 1, 2]])
    r2 = sp.Matrix([[0, 1, 1, 0], [1, 2, 0, 1], [1, 0, -2, 1], [0, 1, 1, 1]])
    r3 = sp.Matrix([[2, 0, 1, 1], [0, 1, 1, 0], [1, 1, 1, 2], [1, 0, 2, -1]])

    def polarized(rows: tuple[sp.Matrix, sp.Matrix, sp.Matrix]) -> sp.Expr:
        x, y, z = rows
        sym3 = (sp.trace(x * y * z) + sp.trace(x * z * y)) / 2
        trace_pair = (
            sp.trace(x) * sp.trace(y * z)
            + sp.trace(y) * sp.trace(x * z)
            + sp.trace(z) * sp.trace(x * y)
        ) / 3
        return sp.expand(
            sp.Rational(503, 648) * sym3
            + sp.Rational(11, 864) * trace_pair
            - sp.Rational(1, 5184) * sp.trace(x) * sp.trace(y) * sp.trace(z)
        )

    values = {
        polarized(tuple(rows[index] for index in permutation))
        for permutation in itertools.permutations(range(3))
        for rows in [(r1, r2, r3)]
    }
    if len(values) != 1:
        raise ValueError("polarized carrier is not S3 invariant")
    diagonal = polarized((r1, r1, r1))
    diagonal_expected = (
        sp.Rational(503, 648) * sp.trace(r1**3)
        + sp.Rational(11, 864) * sp.trace(r1) * sp.trace(r1**2)
        - sp.Rational(1, 5184) * sp.trace(r1) ** 3
    )
    if sp.expand(diagonal - diagonal_expected) != 0:
        raise ValueError("polarized carrier diagonal restriction failed")
    return stored


def main() -> int:
    verify()
    print("independent generic ghost n=3 adiabatic carrier: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
