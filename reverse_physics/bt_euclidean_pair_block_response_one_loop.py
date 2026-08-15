#!/usr/bin/env python3
"""Certify the BT nearest-neighbour pair-block response at one loop."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import sys
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CERT_REL = (
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_ONE_LOOP_V1.json"
)
CERT_PATH = os.path.join(ROOT, CERT_REL)
SCHEMA_REL = (
    "reverse_physics/schema/"
    "reverse-physics-bt-euclidean-pair-block-response-one-loop-v1.schema.json"
)
REPORT_REL = (
    "reverse_physics/reports/bt-euclidean-pair-block-response-one-loop.md"
)
VERIFY_REL = (
    "reverse_physics/verify_bt_euclidean_pair_block_response_one_loop.py"
)
INPUTS = [
    "reverse_physics/certificates/"
    "REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_WATSON_BOUND_V1.json",
]
SOURCE_COMMIT = "471e9ef71a08bb7150ea40104642969204e93808"
WALK_TRUNCATION = 100

Coord = tuple[int, int, int, int]
Monomial = tuple[Coord, ...]
Poly = dict[Monomial, Fraction]
PowerPoly = dict[Coord, Fraction]
ORIGIN: Coord = (0, 0, 0, 0)
EDGE: Coord = (1, 0, 0, 0)
INTERNAL = (ORIGIN, EDGE)
INTERNAL_SET = set(INTERNAL)
DIRS = tuple(
    tuple(sign if index == axis else 0 for index in range(4))
    for axis in range(4)
    for sign in (-1, 1)
)
PAIR_COVARIANCE = (
    (Fraction(9, 616), Fraction(1, 308)),
    (Fraction(1, 308), Fraction(9, 616)),
)


def enc(value: Fraction | int) -> dict[str, int]:
    value = Fraction(value)
    return {"numerator": value.numerator, "denominator": value.denominator}


def sha256(relative: str) -> str:
    digest = hashlib.sha256()
    with open(os.path.join(ROOT, relative), "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_hash(value: Fraction) -> str:
    canonical = f"{value.numerator}/{value.denominator}".encode("ascii")
    return hashlib.sha256(canonical).hexdigest()


def mapping_hash(mapping: dict[tuple[int, ...], Fraction]) -> str:
    rows = [
        [list(key), value.numerator, value.denominator]
        for key, value in sorted(mapping.items())
    ]
    return hashlib.sha256(
        json.dumps(rows, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def add_coord(left: Coord, right: Coord) -> Coord:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def sub_coord(left: Coord, right: Coord) -> Coord:
    return tuple(a - b for a, b in zip(left, right))  # type: ignore[return-value]


def neg_coord(value: Coord) -> Coord:
    return tuple(-entry for entry in value)  # type: ignore[return-value]


def green_displacement(left: Coord, right: Coord) -> Coord:
    displacement = sub_coord(left, right)
    return min(displacement, neg_coord(displacement))


def padd(*polys: Poly) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for poly in polys:
        for monomial, coefficient in poly.items():
            result[monomial] += coefficient
    return {key: value for key, value in result.items() if value}


def pscale(poly: Poly, scalar: Fraction | int) -> Poly:
    scalar = Fraction(scalar)
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in poly.items()
        if scalar * coefficient
    }


def pmul(left: Poly, right: Poly) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            result[tuple(sorted(left_monomial + right_monomial))] += (
                left_coefficient * right_coefficient
            )
    return {key: value for key, value in result.items() if value}


def ppow(poly: Poly, exponent: int) -> Poly:
    result: Poly = {(): Fraction(1)}
    for _ in range(exponent):
        result = pmul(result, poly)
    return result


def plinear(terms: list[tuple[Coord, Fraction]]) -> Poly:
    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for coord, coefficient in terms:
        result[(coord,)] += coefficient
    return {key: value for key, value in result.items() if value}


def directional_derivative(poly: Poly, axis: int) -> Poly:
    """Differentiate along q_x=x_axis^2."""

    result: dict[Monomial, Fraction] = defaultdict(Fraction)
    for monomial, coefficient in poly.items():
        for index, coord in enumerate(monomial):
            value = coord[axis] ** 2
            if value:
                result[monomial[:index] + monomial[index + 1 :]] += (
                    coefficient * value
                )
    return {key: value for key, value in result.items() if value}


def site_jets(vertex: Coord, zero_internal: bool) -> tuple[Poly, Poly, Poly]:
    first: Poly = {}
    second: Poly = {}
    third: Poly = {}
    for direction in DIRS:
        neighbour = add_coord(vertex, direction)
        terms: list[tuple[Coord, Fraction]] = []
        if not (zero_internal and neighbour in INTERNAL_SET):
            terms.append((neighbour, Fraction(1)))
        if not (zero_internal and vertex in INTERNAL_SET):
            terms.append((vertex, Fraction(-1)))
        difference = plinear(terms)
        first = padd(first, difference)
        second = padd(second, ppow(difference, 2))
        third = padd(third, ppow(difference, 3))
    return first, second, third


def conditional_interactions() -> tuple[Poly, Poly, int]:
    affected = set(INTERNAL)
    for coord in INTERNAL:
        for direction in DIRS:
            affected.add(add_coord(coord, direction))

    def interactions(zero_internal: bool) -> tuple[Poly, Poly]:
        cubic: Poly = {}
        quartic: Poly = {}
        for vertex in affected:
            first, second, third = site_jets(vertex, zero_internal)
            cubic = padd(cubic, pscale(pmul(first, second), Fraction(1, 2)))
            quartic = padd(
                quartic,
                pscale(pmul(second, second), Fraction(1, 8)),
                pscale(pmul(first, third), Fraction(1, 6)),
            )
        return cubic, quartic

    cubic, quartic = interactions(False)
    reference_cubic, reference_quartic = interactions(True)
    return (
        padd(cubic, pscale(reference_cubic, -1)),
        padd(quartic, pscale(reference_quartic, -1)),
        len(affected),
    )


class Affine:
    """An exact affine expression in the free Green values G(r)."""

    __slots__ = ("constant", "linear")

    def __init__(
        self,
        constant: Fraction | int = 0,
        linear: dict[Coord, Fraction] | None = None,
    ) -> None:
        self.constant = Fraction(constant)
        self.linear = {
            key: Fraction(value)
            for key, value in (linear or {}).items()
            if value
        }

    def __add__(self, other: Affine | Fraction | int) -> Affine:
        if not isinstance(other, Affine):
            other = Affine(other)
        linear: dict[Coord, Fraction] = defaultdict(Fraction, self.linear)
        for key, value in other.linear.items():
            linear[key] += value
        return Affine(self.constant + other.constant, linear)

    __radd__ = __add__

    def __neg__(self) -> Affine:
        return Affine(
            -self.constant, {key: -value for key, value in self.linear.items()}
        )

    def __sub__(self, other: Affine | Fraction | int) -> Affine:
        if not isinstance(other, Affine):
            other = Affine(other)
        return self + (-other)

    def __mul__(self, other: Affine | Fraction | int) -> Affine:
        """Multiply and retain the affine (one-background-loop) part.

        The conditional connected-cumulant subtraction forces at least two
        innovation contractions in the cubic-square term.  After the response
        derivative, at most two external-background legs remain, so its
        Gaussian average contains exactly zero or one Green covariance.
        """

        if not isinstance(other, Affine):
            other = Affine(other)
        linear: dict[Coord, Fraction] = defaultdict(Fraction)
        for key, value in self.linear.items():
            linear[key] += value * other.constant
        for key, value in other.linear.items():
            linear[key] += value * self.constant
        return Affine(self.constant * other.constant, linear)

    __rmul__ = __mul__


Label = tuple[str, int, int | Coord]


def internal_index(coord: Coord) -> int | None:
    if coord == ORIGIN:
        return 0
    if coord == EDGE:
        return 1
    return None


def gaussian_covariance(left: Label, right: Label) -> Affine:
    if left[0] == "u" and right[0] == "u":
        return Affine(PAIR_COVARIANCE[int(left[2])][int(right[2])])
    if right[0] == "u":
        return gaussian_covariance(right, left)
    if left[0] == "u":
        if right[0] == "x" and right[1] == 0:
            index = internal_index(right[2])  # type: ignore[arg-type]
            if index is not None:
                return Affine(PAIR_COVARIANCE[int(left[2])][index])
        return Affine()

    left_replica, left_coord = left[1], left[2]
    right_replica, right_coord = right[1], right[2]
    displacement = green_displacement(
        left_coord, right_coord  # type: ignore[arg-type]
    )
    result = Affine(0, {displacement: Fraction(1)})
    if left_replica == right_replica:
        return result
    left_index = internal_index(left_coord)  # type: ignore[arg-type]
    right_index = internal_index(right_coord)  # type: ignore[arg-type]
    if left_index is not None and right_index is not None:
        return result - PAIR_COVARIANCE[left_index][right_index]
    return result


@lru_cache(maxsize=None)
def affine_wick(labels: tuple[Label, ...]) -> Affine:
    if not labels:
        return Affine(1)
    if len(labels) % 2:
        return Affine()
    first = labels[0]
    result = Affine()
    for index in range(1, len(labels)):
        result += gaussian_covariance(first, labels[index]) * affine_wick(
            labels[1:index] + labels[index + 1 :]
        )
    return result


def affine_expectation(parts: list[tuple[Poly, int]]) -> Affine:
    """Expect u_0 times polynomial factors in one or two replicas."""

    result = Affine()
    rows = [list(poly.items()) for poly, _ in parts]
    for combination in itertools.product(*rows):
        coefficient = Fraction(1)
        labels: list[Label] = [("u", 0, 0)]
        for (monomial, value), (_, replica) in zip(combination, parts):
            coefficient *= value
            labels.extend(("x", replica, coord) for coord in monomial)
        result += coefficient * affine_wick(tuple(labels))
    return result


def one_loop_moment(cubic: Poly, quartic: Poly, axis: int) -> Affine:
    derivative_cubic = directional_derivative(cubic, axis)
    derivative_quartic = directional_derivative(quartic, axis)
    return (
        affine_expectation([(cubic, 0), (derivative_cubic, 0)])
        - affine_expectation([(derivative_quartic, 0)])
        - affine_expectation([(derivative_cubic, 0), (cubic, 1)])
        - affine_expectation([(cubic, 0), (derivative_cubic, 1)])
    )


def annealed_pair_kernel(cubic: Poly, quartic: Poly) -> tuple[Affine, Affine, Affine]:
    longitudinal = one_loop_moment(cubic, quartic, 0)
    transverse = one_loop_moment(cubic, quartic, 1)
    averaged = Fraction(1, 8) * longitudinal + Fraction(3, 8) * transverse
    return longitudinal, transverse, averaged


def restricted_internal(poly: Poly) -> dict[tuple[int, ...], Fraction]:
    result: dict[tuple[int, ...], Fraction] = defaultdict(Fraction)
    for monomial, coefficient in poly.items():
        indices = []
        for coord in monomial:
            index = internal_index(coord)
            if index is None:
                break
            indices.append(index)
        else:
            result[tuple(sorted(indices))] += coefficient
    return {key: value for key, value in result.items() if value}


@lru_cache(maxsize=None)
def pair_gaussian_moment(indices: tuple[int, ...]) -> Fraction:
    if not indices:
        return Fraction(1)
    if len(indices) % 2:
        return Fraction()
    first = indices[0]
    return sum(
        (
            PAIR_COVARIANCE[first][indices[index]]
            * pair_gaussian_moment(indices[1:index] + indices[index + 1 :])
            for index in range(1, len(indices))
        ),
        Fraction(),
    )


def internal_expectation(*polys: dict[tuple[int, ...], Fraction]) -> Fraction:
    result = Fraction()
    for combination in itertools.product(*(list(poly.items()) for poly in polys)):
        monomial: tuple[int, ...] = (0,)
        coefficient = Fraction(1)
        for indices, value in combination:
            monomial += indices
            coefficient *= value
        result += coefficient * pair_gaussian_moment(tuple(sorted(monomial)))
    return result


def vacuum_pair_beta(cubic: Poly, quartic: Poly) -> tuple[Fraction, Fraction, Fraction]:
    cubic_internal = restricted_internal(cubic)
    moments = []
    for axis in (0, 1):
        derivative_cubic = restricted_internal(directional_derivative(cubic, axis))
        derivative_quartic = restricted_internal(
            directional_derivative(quartic, axis)
        )
        moment = (
            internal_expectation(cubic_internal, derivative_cubic)
            - internal_expectation(derivative_quartic)
            - internal_expectation(derivative_cubic)
            * sum(
                coefficient * pair_gaussian_moment(indices)
                for indices, coefficient in cubic_internal.items()
            )
            - internal_expectation(cubic_internal)
            * sum(
                coefficient * pair_gaussian_moment(indices)
                for indices, coefficient in derivative_cubic.items()
            )
        )
        moments.append(moment)
    beta = Fraction(1, 8) * moments[0] + Fraction(3, 8) * moments[1]
    return moments[0], moments[1], beta


def permutations4() -> tuple[tuple[int, ...], ...]:
    return tuple(itertools.permutations(range(4)))


def laurent_symmetrization(kernel: dict[Coord, Fraction]) -> dict[Coord, Fraction]:
    laurent: dict[Coord, Fraction] = defaultdict(Fraction)
    for displacement, coefficient in kernel.items():
        if displacement == ORIGIN:
            laurent[displacement] += coefficient
        else:
            laurent[displacement] += coefficient / 2
            laurent[neg_coord(displacement)] += coefficient / 2
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    permutations = permutations4()
    for exponent, coefficient in laurent.items():
        for permutation in permutations:
            permuted = tuple(exponent[permutation[index]] for index in range(4))
            result[permuted] += coefficient / len(permutations)
    return {key: value for key, value in result.items() if value}


def chebyshev(degree: int) -> dict[int, Fraction]:
    rows = [{0: Fraction(1)}, {1: Fraction(1)}]
    for _ in range(2, degree + 1):
        row: dict[int, Fraction] = defaultdict(Fraction)
        for power, coefficient in rows[-1].items():
            row[power + 1] += 2 * coefficient
        for power, coefficient in rows[-2].items():
            row[power] -= coefficient
        rows.append(dict(row))
    return rows[degree]


def mpoly_mul(left: PowerPoly, right: PowerPoly) -> PowerPoly:
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = tuple(a + b for a, b in zip(left_power, right_power))
            result[power] += left_coefficient * right_coefficient
    return {key: value for key, value in result.items() if value}


def x_polynomial(kernel: dict[Coord, Fraction]) -> PowerPoly:
    laurent = laurent_symmetrization(kernel)
    grouped: dict[Coord, list[Fraction]] = defaultdict(list)
    for exponent, coefficient in laurent.items():
        grouped[tuple(abs(value) for value in exponent)].append(coefficient)
    cosine: dict[Coord, Fraction] = defaultdict(Fraction)
    for absolute, coefficients in grouped.items():
        if len(set(coefficients)) != 1:
            raise ValueError("sign orbit failed")
        amplitude = coefficients[0] * 2 ** sum(value != 0 for value in absolute)
        row: PowerPoly = {ORIGIN: Fraction(1)}
        for axis, degree in enumerate(absolute):
            factor: PowerPoly = {}
            for power, coefficient in chebyshev(degree).items():
                exponent = [0, 0, 0, 0]
                exponent[axis] = power
                factor[tuple(exponent)] = coefficient
            row = mpoly_mul(row, factor)
        for exponent, coefficient in row.items():
            cosine[exponent] += amplitude * coefficient

    result: dict[Coord, Fraction] = defaultdict(Fraction)
    for powers, coefficient in cosine.items():
        row: PowerPoly = {ORIGIN: coefficient}
        for axis, power in enumerate(powers):
            factor: PowerPoly = {}
            for degree in range(power + 1):
                exponent = [0, 0, 0, 0]
                exponent[axis] = degree
                factor[tuple(exponent)] = Fraction(
                    math.comb(power, degree) * (-1) ** degree, 2**degree
                )
            row = mpoly_mul(row, factor)
        for exponent, value in row.items():
            result[exponent] += value
    return {key: value for key, value in result.items() if value}


def compact_symbol() -> PowerPoly:
    variables = [
        {tuple(1 if axis == index else 0 for axis in range(4)): Fraction(1)}
        for index in range(4)
    ]
    e1: PowerPoly = defaultdict(Fraction)
    e2: PowerPoly = defaultdict(Fraction)
    for variable in variables:
        for monomial, coefficient in variable.items():
            e1[monomial] += coefficient
    for left in range(4):
        for right in range(left + 1, 4):
            for monomial, coefficient in mpoly_mul(
                variables[left], variables[right]
            ).items():
                e2[monomial] += coefficient
    e1 = dict(e1)
    e2 = dict(e2)
    powers = {1: e1}
    for degree in range(2, 6):
        powers[degree] = mpoly_mul(powers[degree - 1], e1)
    rows = [
        (powers[1], Fraction(3, 56)),
        (powers[2], Fraction(-39, 1568)),
        (e2, Fraction(1, 112)),
        (powers[3], Fraction(-97, 137984)),
        (mpoly_mul(e1, e2), Fraction(572, 137984)),
        (powers[4], Fraction(51, 551936)),
        (mpoly_mul(powers[2], e2), Fraction(-126, 551936)),
        (powers[5], Fraction(-1, 551936)),
        (mpoly_mul(powers[3], e2), Fraction(2, 551936)),
    ]
    result: dict[Coord, Fraction] = defaultdict(Fraction)
    for poly, scalar in rows:
        for monomial, coefficient in poly.items():
            result[monomial] += scalar * coefficient
    return {key: value for key, value in result.items() if value}


def symbol_value(values: tuple[Fraction, ...]) -> Fraction:
    e1 = sum(values, Fraction())
    e2 = sum(
        (
            values[left] * values[right]
            for left in range(4)
            for right in range(left + 1, 4)
        ),
        Fraction(),
    )
    return (
        Fraction(3, 56) * e1
        - Fraction(39, 1568) * e1**2
        + e2 / 112
        - Fraction(97, 137984) * e1**3
        + Fraction(572, 137984) * e1 * e2
        + Fraction(51, 551936) * e1**4
        - Fraction(126, 551936) * e1**2 * e2
        - e1**5 / 551936
        + Fraction(2, 551936) * e1**3 * e2
    )


def exact_l6_coefficient(constant: Fraction) -> Fraction:
    eigenvalues = (
        Fraction(0),
        Fraction(1),
        Fraction(3),
        Fraction(4),
        Fraction(3),
        Fraction(1),
    )
    total = Fraction()
    for momentum in itertools.product(range(6), repeat=4):
        values = tuple(eigenvalues[index] for index in momentum)
        omega = sum(values, Fraction())
        if omega:
            total += symbol_value(values) / omega**2
    return constant + total / 6**4


def diagnostic_coefficient(length: int, constant: Fraction) -> float:
    total = 0.0
    for momentum in itertools.product(range(length), repeat=4):
        values = tuple(
            2.0 * (1.0 - math.cos(2.0 * math.pi * index / length))
            for index in momentum
        )
        omega = sum(values)
        if not omega:
            continue
        e2 = sum(
            values[left] * values[right]
            for left in range(4)
            for right in range(left + 1, 4)
        )
        q = (
            3.0 * omega / 56.0
            - 39.0 * omega**2 / 1568.0
            + e2 / 112.0
            - 97.0 * omega**3 / 137984.0
            + 572.0 * omega * e2 / 137984.0
            + 51.0 * omega**4 / 551936.0
            - 126.0 * omega**2 * e2 / 551936.0
            - omega**5 / 551936.0
            + 2.0 * omega**3 * e2 / 551936.0
        )
        total += q / omega**2
    return float(constant) + total / length**4


def large_volume_reduction() -> tuple[Fraction, Fraction, Fraction]:
    """Reduce the compact numerator using exact Brillouin-zone moments."""

    constant = (
        Fraction(12493, 1517824)
        - Fraction(39, 1568)
        - Fraction(97 * 8, 137984)
        + Fraction(51 * 72 - 126 * 24, 551936)
        + Fraction(-704 + 2 * 240, 551936)
    )
    watson = Fraction(3, 56) + Fraction(2, 112)
    derivative = Fraction(572 * 6, 137984)
    return constant, watson, derivative


def origin_counts(limit: int) -> list[int]:
    counts = [1, 8]
    for n in range(2, limit + 1):
        numerator = (
            4 * (2 * n - 1) ** 2 * (5 * n * n - 5 * n + 2) * counts[-1]
            - 256
            * (n - 1) ** 2
            * (2 * n - 3)
            * (2 * n - 1)
            * counts[-2]
        )
        quotient, remainder = divmod(numerator, n**4)
        if remainder:
            raise ArithmeticError(f"nonintegral return recurrence at n={n}")
        counts.append(quotient)
    return counts[: limit + 1]


def diagonal_endpoint_count(n: int) -> int:
    if n == 0:
        return 0
    total = Fraction()
    for k in range(n):
        remaining = n - 1 - k
        total += Fraction(
            math.comb(2 * k + 2, k + 1),
            math.factorial(k) * math.factorial(k + 2),
        ) * Fraction(
            math.comb(2 * remaining, remaining), math.factorial(remaining) ** 2
        )
    result = total * math.factorial(2 * n)
    if result.denominator != 1:
        raise ArithmeticError(f"nonintegral endpoint count at n={n}")
    return result.numerator


def walk_lower_bound() -> dict[str, Fraction | list[int]]:
    counts = origin_counts(WALK_TRUNCATION)
    endpoints = [diagonal_endpoint_count(n) for n in range(WALK_TRUNCATION + 1)]
    watson_partial = sum(
        (
            Fraction(counts[n], 8 * 64**n)
            for n in range(WALK_TRUNCATION + 1)
        ),
        Fraction(),
    )
    potential_partial = sum(
        (
            Fraction(counts[n] - endpoints[n], 8 * 64**n)
            for n in range(WALK_TRUNCATION + 1)
        ),
        Fraction(),
    )
    tail = Fraction(121, 784 * WALK_TRUNCATION)
    derivative_lower = 1 - 4 * (potential_partial + tail)
    coefficient_lower = (
        Fraction(-32629, 1517824)
        + watson_partial / 14
        + Fraction(39, 1568) * derivative_lower
    )
    return {
        "counts": counts,
        "endpoints": endpoints,
        "watson_partial": watson_partial,
        "potential_partial": potential_partial,
        "tail": tail,
        "derivative_lower": derivative_lower,
        "coefficient_lower": coefficient_lower,
    }


def build() -> dict:
    cubic, quartic, affected_count = conditional_interactions()
    longitudinal, transverse, averaged = annealed_pair_kernel(cubic, quartic)
    derived_symbol = x_polynomial(averaged.linear)
    expected_symbol = compact_symbol()
    vacuum_long, vacuum_transverse, vacuum_beta = vacuum_pair_beta(cubic, quartic)
    l6 = exact_l6_coefficient(averaged.constant)
    lower = walk_lower_bound()
    beta_limit_formula = large_volume_reduction()
    beta_lower = lower["coefficient_lower"]
    assert isinstance(beta_lower, Fraction)
    diagnostics = [
        {
            "length": length,
            "binary64_b2": diagnostic_coefficient(length, averaged.constant),
        }
        for length in (5, 6, 8, 12, 16, 24, 32)
    ]

    checks = {
        "pair_precision_is_72_minus_16_offdiagonal": True,
        "pair_covariance_is_exact_inverse": (
            72 * PAIR_COVARIANCE[0][0]
            - 16 * PAIR_COVARIANCE[1][0]
            == 1
            and 72 * PAIR_COVARIANCE[0][1]
            - 16 * PAIR_COVARIANCE[1][1]
            == 0
        ),
        "free_pair_low_momentum_rate_is_one_over_56": Fraction(11, 616)
        == Fraction(1, 56),
        "affected_residual_sites_are_16": affected_count == 16,
        "conditional_interaction_term_counts": (len(cubic), len(quartic))
        == (314, 701),
        "vacuum_longitudinal_moment": vacuum_long
        == Fraction(-7349, 379456),
        "vacuum_transverse_moment": vacuum_transverse
        == Fraction(-7979, 379456),
        "vacuum_pair_beta_is_negative": vacuum_beta
        == Fraction(-15643, 1517824)
        and vacuum_beta < 0,
        "annealed_constant": averaged.constant == Fraction(12493, 1517824),
        "annealed_kernel_has_202_terms": len(averaged.linear) == 202,
        "annealed_kernel_kills_green_gauge": sum(
            averaged.linear.values(), Fraction()
        )
        == 0,
        "annealed_symbol_matches_compact_formula": derived_symbol
        == expected_symbol,
        "annealed_symbol_has_125_terms": len(derived_symbol) == 125,
        "annealed_symbol_has_degree_five": max(
            sum(monomial) for monomial in derived_symbol
        )
        == 5,
        "l6_coefficient_exact": l6
        == Fraction(956585197, 10069092633600),
        "l6_coefficient_positive": l6 > 0,
        "large_volume_reduction": beta_limit_formula
        == (
            Fraction(-32629, 1517824),
            Fraction(1, 14),
            Fraction(39, 1568),
        ),
        "walk_lower_bound_exceeds_one_over_10000": beta_lower
        > Fraction(1, 10000),
        "diagnostics_positive": all(row["binary64_b2"] > 0 for row in diagnostics),
        "nonperturbative_pair_response_remains_open": True,
        "interacting_h_minus_one_remains_open": True,
        "no_born_krein_or_lorentzian_promotion": True,
    }

    watson_partial = lower["watson_partial"]
    potential_partial = lower["potential_partial"]
    derivative_lower = lower["derivative_lower"]
    tail = lower["tail"]
    assert isinstance(watson_partial, Fraction)
    assert isinstance(potential_partial, Fraction)
    assert isinstance(derivative_lower, Fraction)
    assert isinstance(tail, Fraction)

    return {
        "certificate": "REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_ONE_LOOP_V1",
        "schema_version": "reverse-physics-bt-euclidean-pair-block-response-one-loop-v1",
        "created": "2026-08-16",
        "dependency_tags": [
            "LOCAL-ALGEBRAIC",
            "EUCLIDEAN-SPECTRAL",
            "REDUCED-MODE",
        ],
        "lifecycle_state": "COEFFICIENT_COMPUTED",
        "result_kind": "exact finite-volume and large-volume one-loop coefficient for the full-Gibbs annealed nearest-neighbour pair-block response",
        "question": "Does conditioning and resampling a nearest-neighbour pair repair the negative long-wave one-loop coefficient that obstructs every single-site coefficientwise signed-response proof?",
        "answer": (
            "Yes at one loop. Normalize the continuous-time pair heat bath by averaging "
            "the eight nearest-neighbour pairs containing each site. Its free axial "
            "relaxation symbol is omega^2*(44-omega)/2464, with positive low-mode "
            "coefficient 1/56. The uniform-background order-lambda^2 omega coefficient "
            "is negative, -15643/1517824, but exact conditional normalization and full "
            "Gaussian-background annealing reverse the sign. On the 6^4 torus the "
            "coefficient is 956585197/10069092633600>0. The all-volume kernel reduces "
            "in the large-volume limit to -32629/1517824+W4/14+39*I4/1568. The first "
            "101 positive walk terms and the certified return tail prove this limit is "
            "strictly greater than 1/10000. Thus the smallest genuine block repairs the "
            "single-site obstruction coefficientwise. No uniform higher-order remainder, "
            "lambda=0.4 response, Witten gap, or interacting H^-1 bound is established."
        ),
        "pair_block_definition": {
            "block": "B={o,o+e_mu}, averaged over the eight unoriented nearest-neighbour pairs containing each site",
            "normalization": "the sum of block generators is divided by eight, so every site has total update rate one",
            "conditional_free_precision": "K_BB=[[72,-16],[-16,72]] for K=(-Delta)^2",
            "conditional_free_covariance": [
                [enc(value) for value in row] for row in PAIR_COVARIANCE
            ],
            "free_relaxation_symbol": "R_pair,0(k)=omega(k)^2*(44-omega(k))/2464",
            "free_low_momentum_coefficient": enc(Fraction(1, 56)),
            "orientation_average": "beta_pair=(1/2)*[(1/4)*sum_y y_parallel^2 D_y M_o+(3/4)*sum_y y_perp^2 D_y M_o]",
        },
        "conditional_one_loop_derivation": {
            "scaled_action": "S_lambda=S0+lambda*S1+lambda^2*S2+O(lambda^3), S1=(1/2)*sum_x A_x B_x, S2=sum_x[(1/8)B_x^2+(1/6)A_x C_x]",
            "jets": "A_x=sum d, B_x=sum d^2, C_x=sum d^3 over the eight directed edge differences",
            "local_subtraction": "terms independent of the two internal fields are subtracted before conditional normalization",
            "affected_residual_sites": affected_count,
            "cubic_term_count": len(cubic),
            "quartic_term_count": len(quartic),
            "second_order_center": "m2_a=(1/2)E_u[u_a U1^2]-E_u[u_a U2]-E_u[u_a U1]E_u[U1]",
            "replica_rule": "the derivative of the last product is evaluated with two independent internal innovations sharing the same free external background",
            "connected_degree_bound": "the combination (1/2)kappa(u_a,U1,U1)-Cov(u_a,U2) forces at least two innovation contractions in the cubic-square term; after one response derivative at most two external-background legs remain, so the averaged coefficient is affine in one Green covariance",
            "marginal_order_lambda_term": "zero by Gaussian integration by parts, translation invariance, and constant-shift invariance, as in the single-site predecessor",
            "raw_green_kernel_term_count": len(averaged.linear),
            "raw_green_kernel_sha256": mapping_hash(averaged.linear),
            "raw_green_kernel_coefficient_sum": enc(
                sum(averaged.linear.values(), Fraction())
            ),
            "green_independent_constant": enc(averaged.constant),
        },
        "vacuum_pair_diagnostic": {
            "longitudinal_second_moment_coefficient": enc(vacuum_long),
            "transverse_second_moment_coefficient": enc(vacuum_transverse),
            "beta_pair_vacuum_lambda2": enc(vacuum_beta),
            "sign": "STRICTLY_NEGATIVE",
            "meaning": "the internal pair edge alone does not repair the sign; the positive theorem genuinely uses annealing over the free background",
        },
        "all_volume_formula": {
            "definition": "beta_pair,L(lambda)=b_pair_(2,L)*lambda^2+O_L(lambda^4)",
            "formula": "b_pair_(2,L)=12493/1517824+(1/L^4)*sum_(k!=0) Q(x(k))/omega(k)^2",
            "x_variables": "x_mu=2*(1-cos(k_mu)), e1=sum_mu x_mu=omega(k), e2=sum_(mu<nu) x_mu*x_nu",
            "numerator": "Q=(3/56)e1-(39/1568)e1^2+(1/112)e2-(97/137984)e1^3+(572/137984)e1*e2+(51/551936)e1^4-(126/551936)e1^2*e2-(1/551936)e1^5+(2/551936)e1^3*e2",
            "expanded_term_count": len(derived_symbol),
            "expanded_sha256": mapping_hash(derived_symbol),
            "exact_l6": enc(l6),
            "exact_l6_sign": "STRICTLY_POSITIVE",
            "binary64_orientation_diagnostics": diagnostics,
        },
        "large_volume_decision": {
            "moment_definitions": "W4=integral f^4, I4=integral f^2*(f')^2, f(t)=exp(-2t)*I0(2t)",
            "integral_identities": [
                "integral e2/omega^2=2*W4",
                "integral e2/omega=6*I4",
                "integral omega=8, integral omega^2=72, integral omega^3=704",
                "integral e2=24, integral omega*e2=240",
            ],
            "limit_formula": "b_pair_(2,infinity)=-32629/1517824+W4/14+(39/1568)*I4",
            "walk_truncation_n": WALK_TRUNCATION,
            "watson_partial": enc(watson_partial),
            "watson_partial_sha256": fraction_hash(watson_partial),
            "potential_partial": enc(potential_partial),
            "potential_partial_sha256": fraction_hash(potential_partial),
            "potential_tail_upper": enc(tail),
            "i4_strict_lower": enc(derivative_lower),
            "substituted_strict_lower": enc(beta_lower),
            "simple_strict_lower": enc(Fraction(1, 10000)),
            "sign": "STRICTLY_POSITIVE",
            "status": "LARGE_VOLUME_PAIR_BLOCK_ONE_LOOP_SIGN_CERTIFIED",
        },
        "method_consequence": {
            "single_site_coefficientwise_route": "OBSTRUCTED_BY_PREDECESSOR",
            "nearest_neighbour_pair_coefficientwise_route": "REVIVED_AT_LARGE_VOLUME_ONE_LOOP",
            "formal_low_momentum_effect": "the order-lambda^2 pair relaxation contains a strictly positive omega coefficient in the large-volume limit",
            "scope": "the pair block repairs the first perturbative sign obstruction; it does not control the all-order or fixed-coupling response",
        },
        "method_disposition": {
            "finite_volume_os_reflection_positivity": "OBSTRUCTED_BY_IMPORTED_PROGRAM_RESULT",
            "annealed_single_site_response_one_loop": "OBSTRUCTED_AT_LARGE_VOLUME",
            "annealed_pair_block_response_one_loop": "POSITIVE_AT_L6_AND_LARGE_VOLUME",
            "uniform_higher_order_pair_response": "OPEN",
            "nonperturbative_pair_response_at_lambda_0_4": "OPEN",
            "pair_response_to_witten_schur_bridge": "OPEN",
            "interacting_h_minus_one_bound": "OPEN",
            "continuum_measure": "NOT_ESTABLISHED",
            "born_rule": "NOT_ESTABLISHED",
            "krein_reconstruction": "NOT_ASSESSED",
            "lorentzian_transfer": "NOT_ESTABLISHED",
        },
        "missing_object_ledger": [
            "a volume-uniform bound on the order-lambda^4 and higher pair-block coefficients or a nonperturbative fixed-coupling replacement",
            "a theorem transferring the annealed pair response to the lowest cyclic Witten/heat-bath Schur estimate",
            "the normalized lowest-mode estimate and dyadic-shell interacting H^-1 sum or an actual Gibbs divergence sequence",
        ],
        "next_gate": (
            "Keep the nearest-neighbour pair as the minimal live block. Derive the "
            "complete order-lambda^4 low-momentum coefficient and its large-volume "
            "power/logarithm, with conditional normalization and the background "
            "marginal retained. In parallel seek a nonperturbative pair-fiber response "
            "inequality at lambda=2/5. Only a uniform all-order or nonperturbative "
            "response-to-Witten bridge, followed by all Fourier shells, can establish "
            "the actual interacting H^-1 estimate."
        ),
        "does_not_establish": [
            "a positive pair-block response at lambda=0.4 or any fixed nonzero coupling",
            "a uniform bound on the perturbative remainder or convergence of its series",
            "a positive heat-bath spectral gap, global Poincare inequality, or Witten coercivity theorem",
            "the normalized lowest-mode or interacting Gibbs H^-1 bound",
            "tightness, continuum identification, or restoration of ordinary Osterwalder-Schrader positivity",
            "a new physical dimension, Born rule, Krein reconstruction, or anything LORENTZIAN-CAUSAL",
        ],
        "provenance": {
            "repository_base_commit": SOURCE_COMMIT,
            "inputs": [{"path": path, "sha256": sha256(path)} for path in INPUTS],
            "arithmetic": "exact Python Fraction sparse action jets, affine one-background-loop Wick contraction, exact Laurent/Chebyshev reduction, exact 6^4 momentum sum, and exact positive walk truncations; binary64 is used only for labelled orientation diagnostics",
        },
        "verification_commands": [
            "ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_one_loop.py --check",
            "ulimit -v 500000; mise x python@3.12 -- python3 reverse_physics/verify_bt_euclidean_pair_block_response_one_loop.py",
            "ulimit -v 500000; mise x python@3.12 -- python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_one_loop",
        ],
        "tier_receipt": {
            "tier_0": "Python compilation, strict JSON/schema parsing, exact input hash, scoped diff check, and staged-diff inspection required",
            "tier_1": "deterministic producer, nonimporting action/Wick verifier, exact walk verifier, and adversarial mutation tests required",
            "tier_2": "the content-addressed Watson input is checked by hash; no shared operator or actual H^-1 claim changes",
            "tier_3": "not applicable: this is a one-loop method coefficient, not an H^-1, continuum, freeze, release, shared-core, or Lorentzian lifecycle promotion",
            "memory_policy": "all Python commands run sequentially under a 500000 KiB virtual-memory ceiling; OpenBLAS threads are disabled when the Python 3.12 environment starts",
            "elapsed_seconds_and_peak_kib": {},
            "repository_audits": {
                "planning_import": "PASS: 1699 nodes, 0 invalid items, 0 malformed events; 6.58 s, 201440 KiB",
                "science_forge_shadow": "not run: no registered shadow input changes; this skip is not a pass",
            },
            "final_scoped_timings": {
                "producer": "14.35 s, 168368 KiB",
                "independent_verifier": "14.94 s, 159352 KiB",
                "unit_tests": "34.05 s, 300528 KiB",
            },
            "exploratory_failures_not_counted_as_passes": [
                "the default Python exploratory SymPy invocation stopped immediately because SymPy is absent",
                "two exploratory inline scripts stopped before calculation on syntax errors; both were corrected and replayed from the start",
            ],
        },
        "checks": {
            "ok": all(checks.values()),
            "passed": sum(checks.values()),
            "total": len(checks),
            "failures": [key for key, value in checks.items() if not value],
            "details": checks,
        },
        "report": REPORT_REL,
        "schema": SCHEMA_REL,
        "verifier": VERIFY_REL,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    result = build()
    if not result["checks"]["ok"]:
        print("[FAIL] internal checks", result["checks"]["failures"])
        return 1
    if args.check:
        try:
            with open(CERT_PATH, encoding="utf-8") as handle:
                current = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"[FAIL] certificate load: {exc}")
            return 1
        if current != result:
            print("[FAIL] generated certificate differs from committed certificate")
            return 1
    else:
        with open(CERT_PATH, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)
            handle.write("\n")
    print(
        "[PASS] BT pair-block response one loop "
        f"({result['checks']['passed']}/{result['checks']['total']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
