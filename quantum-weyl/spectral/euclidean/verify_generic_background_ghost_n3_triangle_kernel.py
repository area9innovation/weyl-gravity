#!/usr/bin/env python3
"""Independent direct-integrand replay of the generic ghost n=3 triangle."""

from __future__ import annotations

from fractions import Fraction
import itertools
import json
import math

import sympy as sp

from .generic_background_ghost_n3_triangle_kernel import OUTPUT, build


def _f(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


def _direct(p: sp.Matrix, ks: tuple[sp.Matrix, sp.Matrix, sp.Matrix], rs: tuple[sp.Matrix, sp.Matrix, sp.Matrix]) -> sp.Expr:
    q = (p, p + ks[0], p - ks[2])
    identity = sp.eye(4)
    propagators = []
    for momentum in q:
        denominator = (momentum.T * momentum)[0]
        propagators.append((identity - sp.Rational(1, 3) * momentum * momentum.T / denominator) / denominator)
    return sp.factor(sp.trace(propagators[0] * rs[0] * propagators[1] * rs[1] * propagators[2] * rs[2]))


def _expanded(p: sp.Matrix, ks: tuple[sp.Matrix, sp.Matrix, sp.Matrix], rs: tuple[sp.Matrix, sp.Matrix, sp.Matrix]) -> sp.Expr:
    q = (p, p + ks[0], p - ks[2])
    denominators = tuple((momentum.T * momentum)[0] for momentum in q)
    total = 0
    for bits in itertools.product((0, 1), repeat=3):
        factors = []
        denominator = sp.prod(denominators)
        for index, bit in enumerate(bits):
            factors.append((q[index] * q[index].T if bit else sp.eye(4)) * rs[index])
            if bit:
                denominator *= denominators[index]
        total += (-sp.Rational(1, 3)) ** sum(bits) * sp.trace(sp.prod(factors)) / denominator
    return sp.factor(total)


def verify() -> dict:
    stored = json.loads(OUTPUT.read_text())
    if stored != build():
        raise ValueError("n=3 triangle certificate is stale")
    p = sp.Matrix([1, 2, -1, 3])
    k1 = sp.Matrix([2, -1, 1, 0])
    k2 = sp.Matrix([-1, 2, 0, 1])
    k3 = -k1 - k2
    r1 = sp.Matrix([[1, 1, 0, 0], [1, -1, 1, 0], [0, 1, 2, 1], [0, 0, 1, 0]])
    r2 = sp.Matrix([[0, 1, 1, 0], [1, 2, 0, 1], [1, 0, -1, 0], [0, 1, 0, 1]])
    r3 = sp.Matrix([[2, 0, 1, 1], [0, 1, 1, 0], [1, 1, 0, 2], [1, 0, 2, -2]])
    ks = (k1, k2, k3)
    rs = (r1, r2, r3)
    if sp.factor(_direct(p, ks, rs) - _expanded(p, ks, rs)) != 0:
        raise ValueError("eight-sector direct integrand identity failed")
    if sp.factor(_direct(p, ks, rs) - _direct(p + k1, (k2, k3, k1), (r2, r3, r1))) != 0:
        raise ValueError("cyclic triangle covariance failed")

    alpha1, alpha2 = sp.symbols("alpha1 alpha2")
    alpha0 = 1 - alpha1 - alpha2
    shift_rows = (
        -alpha1 * k1 + alpha2 * k3,
        (1 - alpha1) * k1 + alpha2 * k3,
        -alpha1 * k1 - (1 - alpha2) * k3,
    )
    if any(
        sp.expand(component) != 0
        for component in alpha0 * shift_rows[0]
        + alpha1 * shift_rows[1]
        + alpha2 * shift_rows[2]
    ):
        raise ValueError("triangle barycentric shift identity failed")
    ell = sp.Matrix(sp.symbols("ell0:4"))
    completed_square = sum(
        alpha * ((ell + shift).T * (ell + shift))[0]
        for alpha, shift in zip((alpha0, alpha1, alpha2), shift_rows)
    )
    delta = (
        alpha0 * alpha1 * (k1.T * k1)[0]
        + alpha1 * alpha2 * (k2.T * k2)[0]
        + alpha2 * alpha0 * (k3.T * k3)[0]
    )
    if sp.expand(completed_square - (ell.T * ell)[0] - delta) != 0:
        raise ValueError("triangle Feynman-simplex completion failed")

    sectors = stored["projector_sector_expansion"]["sectors"]
    if len(sectors) != 8 or sum(len(row["wick_rows"]) for row in sectors) != 20:
        raise ValueError("triangle sector/Wick count failed")
    for row in sectors:
        bits = tuple(map(int, row["subset_bits"]))
        size = sum(bits)
        if row["denominator_powers"] != [1 + bit for bit in bits]:
            raise ValueError("triangle denominator powers drifted")
        if _f(row["projector_coefficient"]) != Fraction(-1, 3) ** size:
            raise ValueError("triangle projector coefficient drifted")
        for pair_count, wick in enumerate(row["wick_rows"]):
            expected = Fraction(math.factorial(size - pair_count), 2**pair_count)
            if (
                _f(wick["coefficient_per_pairing"]) != expected
                or wick["Delta_power"] != pair_count - size - 1
                or wick["homogeneous_loop_degree"] != 2 * pair_count
            ):
                raise ValueError("triangle Wick coefficient drifted")
    if stored["carrier_projection"]["repository_I10_projection"] != "NOT_COMPUTED":
        raise ValueError("triangle crossed repository carrier boundary")
    return stored


def main() -> int:
    verify()
    print("independent generic ghost n=3 triangle kernel: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
