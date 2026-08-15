#!/usr/bin/env python3
"""Exact arbitrary-jet evaluator for the polarized pure-Weyl Euler density.

This is an evaluative prototype, not yet the portable component AST required
by Gate A.  It uses the quotient ``Q[a,b]/(a^2,b^2)`` together with normalized
coordinate Taylor coefficients.  Therefore the ``a*b`` coefficient is the
polarized second variation with no hidden factorial, while every arithmetic
operation remains exact over ``fractions.Fraction``.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations, product
from math import isqrt
from typing import Iterable, Mapping, Sequence


DIMENSION = 4
ZERO_MULTIINDEX = (0,) * DIMENSION
PAIRS = tuple((a, b) for a in range(DIMENSION) for b in range(a, DIMENSION))
CoordinateJet = Mapping[tuple[int, int, int, int], Fraction | int]
MetricJets = Mapping[tuple[int, int], CoordinateJet]


def _q(value: Fraction | int) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _degree(alpha: Sequence[int]) -> int:
    return sum(alpha)


@dataclass(frozen=True)
class Jet:
    """Truncated coordinate and square-free bivariate parameter series."""

    order: int
    terms: tuple[tuple[int, int, tuple[int, int, int, int], Fraction], ...] = ()

    @staticmethod
    def from_terms(order: int, terms: Iterable[tuple[int, int, Sequence[int], Fraction | int]]) -> "Jet":
        if order < 0:
            return Jet(-1)
        combined: dict[tuple[int, int, tuple[int, int, int, int]], Fraction] = {}
        for a_degree, b_degree, alpha, coefficient in terms:
            alpha = tuple(int(item) for item in alpha)
            if len(alpha) != DIMENSION or min(alpha) < 0:
                raise ValueError("coordinate multiindex must contain four nonnegative entries")
            if a_degree not in (0, 1) or b_degree not in (0, 1) or _degree(alpha) > order:
                continue
            coefficient = _q(coefficient)
            if coefficient:
                key = (a_degree, b_degree, alpha)
                combined[key] = combined.get(key, Fraction(0)) + coefficient
        return Jet(order, tuple((*key, value) for key, value in sorted(combined.items()) if value))

    @staticmethod
    def zero(order: int) -> "Jet":
        return Jet(order)

    @staticmethod
    def constant(order: int, value: Fraction | int) -> "Jet":
        return Jet.from_terms(order, ((0, 0, ZERO_MULTIINDEX, value),))

    @staticmethod
    def coordinate_series(order: int, coefficients: CoordinateJet, parameter: str | None = None) -> "Jet":
        degrees = {None: (0, 0), "a": (1, 0), "b": (0, 1)}
        if parameter not in degrees:
            raise ValueError("parameter must be None, 'a', or 'b'")
        a_degree, b_degree = degrees[parameter]
        return Jet.from_terms(order, ((a_degree, b_degree, alpha, coefficient) for alpha, coefficient in coefficients.items()))

    @property
    def constant_term(self) -> Fraction:
        return next((value for a, b, alpha, value in self.terms if a == b == 0 and alpha == ZERO_MULTIINDEX), Fraction(0))

    def coefficient(self, a_degree: int, b_degree: int, alpha: Sequence[int] = ZERO_MULTIINDEX) -> Fraction:
        alpha = tuple(alpha)
        return next((value for a, b, word, value in self.terms if (a, b, word) == (a_degree, b_degree, alpha)), Fraction(0))

    def truncate(self, order: int) -> "Jet":
        order = min(order, self.order)
        return Jet.from_terms(order, self.terms)

    def __add__(self, other: "Jet") -> "Jet":
        order = min(self.order, other.order)
        return Jet.from_terms(order, (*self.truncate(order).terms, *other.truncate(order).terms))

    def __neg__(self) -> "Jet":
        return Jet.from_terms(self.order, ((a, b, alpha, -value) for a, b, alpha, value in self.terms))

    def __sub__(self, other: "Jet") -> "Jet":
        return self + (-other)

    def scale(self, value: Fraction | int) -> "Jet":
        value = _q(value)
        return Jet.from_terms(self.order, ((a, b, alpha, value * coefficient) for a, b, alpha, coefficient in self.terms))

    def __mul__(self, other: "Jet") -> "Jet":
        order = min(self.order, other.order)
        terms = []
        for a1, b1, alpha1, value1 in self.terms:
            for a2, b2, alpha2, value2 in other.terms:
                a_degree, b_degree = a1 + a2, b1 + b2
                if a_degree > 1 or b_degree > 1:
                    continue
                alpha = tuple(alpha1[index] + alpha2[index] for index in range(DIMENSION))
                if _degree(alpha) <= order:
                    terms.append((a_degree, b_degree, alpha, value1 * value2))
        return Jet.from_terms(order, terms)

    def derivative(self, axis: int) -> "Jet":
        if not 0 <= axis < DIMENSION:
            raise ValueError("derivative axis out of range")
        if self.order <= 0:
            return Jet.zero(self.order - 1)
        terms = []
        for a_degree, b_degree, alpha, value in self.terms:
            if alpha[axis]:
                lowered = list(alpha)
                multiplier = lowered[axis]
                lowered[axis] -= 1
                terms.append((a_degree, b_degree, tuple(lowered), multiplier * value))
        return Jet.from_terms(self.order - 1, terms)

    def reciprocal(self) -> "Jet":
        constant = self.constant_term
        if not constant:
            raise ZeroDivisionError("series has no invertible constant term")
        one = Jet.constant(self.order, 1)
        reduced = (self.scale(Fraction(1, constant)) - one)
        output = one
        power = one
        for exponent in range(1, self.order + 3):
            power = power * reduced
            output = output + power.scale(-1 if exponent % 2 else 1)
        return output.scale(Fraction(1, constant))

    def sqrt(self) -> "Jet":
        constant = self.constant_term
        numerator_root = isqrt(constant.numerator)
        denominator_root = isqrt(constant.denominator)
        if numerator_root * numerator_root != constant.numerator or denominator_root * denominator_root != constant.denominator:
            raise ValueError("series square root requires a rational-square constant term")
        root = Fraction(numerator_root, denominator_root)
        one = Jet.constant(self.order, 1)
        reduced = self.scale(Fraction(1, constant)) - one
        output = one
        power = one
        coefficient = Fraction(1)
        for exponent in range(1, self.order + 3):
            power = power * reduced
            coefficient *= Fraction(3 - 2 * exponent, 2 * exponent)
            output = output + power.scale(coefficient)
        return output.scale(root)

    def swap_parameters(self) -> "Jet":
        return Jet.from_terms(self.order, ((b, a, alpha, value) for a, b, alpha, value in self.terms))

    def exact_payload(self, a_degree: int = 1, b_degree: int = 1) -> list[dict[str, object]]:
        return [
            {"multiindex": list(alpha), "coefficient": str(value)}
            for a, b, alpha, value in self.terms
            if a == a_degree and b == b_degree
        ]


def sum_jets(values: Iterable[Jet], order: int | None = None) -> Jet:
    values = tuple(values)
    if not values:
        if order is None:
            raise ValueError("empty sum requires an order")
        return Jet.zero(order)
    target = min(value.order for value in values) if order is None else min(order, *(value.order for value in values))
    return Jet.from_terms(target, (term for value in values for term in value.truncate(target).terms))


def _component(jets: MetricJets, pair: tuple[int, int]) -> CoordinateJet:
    return jets.get(tuple(sorted(pair)), {})


def cylinder_background(order: int = 4) -> dict[tuple[int, int], Jet]:
    """Unit ``R x S3`` about chi=theta=pi/2 with rational coefficient jets."""

    cos2_x = Jet.coordinate_series(order, {ZERO_MULTIINDEX: 1, (0, 2, 0, 0): -1, (0, 4, 0, 0): Fraction(1, 3)})
    cos2_y = Jet.coordinate_series(order, {ZERO_MULTIINDEX: 1, (0, 0, 2, 0): -1, (0, 0, 4, 0): Fraction(1, 3)})
    diagonal = {0: Jet.constant(order, -1), 1: Jet.constant(order, 1), 2: cos2_x, 3: cos2_x * cos2_y}
    return {(a, b): diagonal[a] if a == b else Jet.zero(order) for a, b in product(range(DIMENSION), repeat=2)}


def flat_background(order: int = 4) -> dict[tuple[int, int], Jet]:
    diagonal = (-1, 1, 1, 1)
    return {(a, b): Jet.constant(order, diagonal[a]) if a == b else Jet.zero(order) for a, b in product(range(DIMENSION), repeat=2)}


def brinkmann_background(order: int = 4) -> dict[tuple[int, int], Jet]:
    """Flat ``2 du dv + dx^2 + dy^2`` background for the pp-wave benchmark."""

    output = {(a, b): Jet.zero(order) for a, b in product(range(DIMENSION), repeat=2)}
    output[(0, 1)] = output[(1, 0)] = Jet.constant(order, 1)
    output[(2, 2)] = output[(3, 3)] = Jet.constant(order, 1)
    return output


def perturbed_metric(background: Mapping[tuple[int, int], Jet], left: MetricJets, right: MetricJets) -> dict[tuple[int, int], Jet]:
    order = min(item.order for item in background.values())
    return {
        (a, b): background[(a, b)]
        + Jet.coordinate_series(order, _component(left, (a, b)), "a")
        + Jet.coordinate_series(order, _component(right, (a, b)), "b")
        for a, b in product(range(DIMENSION), repeat=2)
    }


def determinant(matrix: Mapping[tuple[int, int], Jet]) -> Jet:
    order = min(value.order for value in matrix.values())
    terms = []
    for permutation in permutations(range(DIMENSION)):
        inversions = sum(permutation[a] > permutation[b] for a in range(DIMENSION) for b in range(a + 1, DIMENSION))
        value = Jet.constant(order, -1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            value = value * matrix[(row, column)]
        terms.append(value)
    return sum_jets(terms)


def inverse_matrix(matrix: Mapping[tuple[int, int], Jet]) -> dict[tuple[int, int], Jet]:
    order = min(value.order for value in matrix.values())
    work = [[matrix[(row, column)] for column in range(DIMENSION)] for row in range(DIMENSION)]
    inverse = [[Jet.constant(order, row == column) for column in range(DIMENSION)] for row in range(DIMENSION)]
    for column in range(DIMENSION):
        pivot = next((row for row in range(column, DIMENSION) if work[row][column].constant_term), None)
        if pivot is None:
            raise ZeroDivisionError("background metric is singular")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            inverse[column], inverse[pivot] = inverse[pivot], inverse[column]
        scale = work[column][column].reciprocal()
        work[column] = [item * scale for item in work[column]]
        inverse[column] = [item * scale for item in inverse[column]]
        for row in range(DIMENSION):
            if row == column:
                continue
            factor = work[row][column]
            work[row] = [work[row][entry] - factor * work[column][entry] for entry in range(DIMENSION)]
            inverse[row] = [inverse[row][entry] - factor * inverse[column][entry] for entry in range(DIMENSION)]
    return {(row, column): inverse[row][column] for row, column in product(range(DIMENSION), repeat=2)}


def _connection(metric: Mapping[tuple[int, int], Jet], inverse: Mapping[tuple[int, int], Jet]) -> dict[tuple[int, int, int], Jet]:
    output = {}
    for target, left, right in product(range(DIMENSION), repeat=3):
        output[(target, left, right)] = sum_jets(
            (
                inverse[(target, index)]
                * (
                    metric[(index, right)].derivative(left)
                    + metric[(index, left)].derivative(right)
                    - metric[(left, right)].derivative(index)
                ).scale(Fraction(1, 2))
                for index in range(DIMENSION)
            ),
            order=3,
        )
    return output


def _geometry(metric: Mapping[tuple[int, int], Jet]) -> dict[str, object]:
    inverse = inverse_matrix(metric)
    gamma = _connection(metric, inverse)
    riemann = {}
    for target, vector, first, second in product(range(DIMENSION), repeat=4):
        riemann[(target, vector, first, second)] = (
            gamma[(target, second, vector)].derivative(first)
            - gamma[(target, first, vector)].derivative(second)
            + sum_jets(
                (
                    gamma[(middle, second, vector)] * gamma[(target, first, middle)]
                    - gamma[(middle, first, vector)] * gamma[(target, second, middle)]
                    for middle in range(DIMENSION)
                ),
                order=2,
            )
        ).truncate(2)
    ricci = {
        (a, b): sum_jets((riemann[(index, a, index, b)] for index in range(DIMENSION)), order=2)
        for a, b in product(range(DIMENSION), repeat=2)
    }
    scalar = sum_jets((inverse[(a, b)] * ricci[(a, b)] for a, b in product(range(DIMENSION), repeat=2)), order=2)
    return {"metric": metric, "inverse": inverse, "connection": gamma, "riemann": riemann, "ricci": ricci, "scalar": scalar}


def _schouten_and_weyl(geometry: Mapping[str, object]) -> tuple[dict[tuple[int, int], Jet], dict[tuple[int, int, int, int], Jet]]:
    metric = geometry["metric"]
    riemann = geometry["riemann"]
    ricci = geometry["ricci"]
    scalar = geometry["scalar"]
    assert isinstance(metric, Mapping) and isinstance(riemann, Mapping) and isinstance(ricci, Mapping) and isinstance(scalar, Jet)
    schouten = {
        (a, b): (ricci[(a, b)] - metric[(a, b)] * scalar.scale(Fraction(1, 6))).scale(Fraction(1, 2)).truncate(2)
        for a, b in product(range(DIMENSION), repeat=2)
    }
    weyl = {}
    for a, b, c, d in product(range(DIMENSION), repeat=4):
        lowered = sum_jets((metric[(a, target)] * riemann[(target, b, c, d)] for target in range(DIMENSION)), order=2)
        correction = (
            metric[(a, c)] * schouten[(d, b)]
            - metric[(a, d)] * schouten[(c, b)]
            - metric[(b, c)] * schouten[(d, a)]
            + metric[(b, d)] * schouten[(c, a)]
        )
        weyl[(a, b, c, d)] = (lowered - correction).truncate(2)
    return schouten, weyl


def _bach_lower(geometry: Mapping[str, object]) -> dict[tuple[int, int], Jet]:
    inverse = geometry["inverse"]
    gamma = geometry["connection"]
    assert isinstance(inverse, Mapping) and isinstance(gamma, Mapping)
    schouten, weyl = _schouten_and_weyl(geometry)
    first_schouten = {}
    for axis, first, second in product(range(DIMENSION), repeat=3):
        first_schouten[(axis, first, second)] = (
            schouten[(first, second)].derivative(axis)
            - sum_jets(
                (
                    gamma[(replacement, axis, first)] * schouten[(replacement, second)]
                    + gamma[(replacement, axis, second)] * schouten[(first, replacement)]
                    for replacement in range(DIMENSION)
                ),
                order=1,
            )
        ).truncate(1)
    cotton = {
        (inner, first, second): first_schouten[(inner, first, second)] - first_schouten[(first, second, inner)]
        for inner, first, second in product(range(DIMENSION), repeat=3)
    }
    divergence = {}
    for first, second in product(range(DIMENSION), repeat=2):
        contracted = []
        for outer, inner in product(range(DIMENSION), repeat=2):
            derivative = cotton[(inner, first, second)].derivative(outer) - sum_jets(
                (
                    gamma[(replacement, outer, inner)] * cotton[(replacement, first, second)]
                    + gamma[(replacement, outer, first)] * cotton[(inner, replacement, second)]
                    + gamma[(replacement, outer, second)] * cotton[(inner, first, replacement)]
                    for replacement in range(DIMENSION)
                ),
                order=0,
            )
            contracted.append(inverse[(outer, inner)] * derivative)
        divergence[(first, second)] = sum_jets(contracted, order=0)
    schouten_up = {
        (first, second): sum_jets(
            (
                inverse[(first, left)] * inverse[(second, right)] * schouten[(left, right)]
                for left, right in product(range(DIMENSION), repeat=2)
            ),
            order=0,
        )
        for first, second in product(range(DIMENSION), repeat=2)
    }
    algebraic = {
        (first, second): sum_jets(
            (schouten_up[(inner, outer)] * weyl[(first, inner, second, outer)] for inner, outer in product(range(DIMENSION), repeat=2)),
            order=0,
        )
        for first, second in product(range(DIMENSION), repeat=2)
    }
    return {(first, second): (divergence[(first, second)] + algebraic[(first, second)]).truncate(0) for first, second in product(range(DIMENSION), repeat=2)}


def _bach_euler_density_jets(
    left: MetricJets,
    right: MetricJets,
    *,
    background: Mapping[tuple[int, int], Jet] | None = None,
) -> tuple[dict[tuple[int, int], Jet], dict[tuple[int, int], Jet]]:
    """Return the perturbed metric and action-normalized Euler density jets."""

    background = cylinder_background(4) if background is None else background
    metric = perturbed_metric(background, left, right)
    geometry = _geometry(metric)
    inverse = geometry["inverse"]
    assert isinstance(inverse, Mapping)
    bach_action = {pair: value.scale(-2) for pair, value in _bach_lower(geometry).items()}
    volume = determinant(metric).scale(-1).sqrt().truncate(0)
    output: dict[tuple[int, int], Jet] = {}
    for first, second in product(range(DIMENSION), repeat=2):
        output[(first, second)] = volume * sum_jets(
            (
                inverse[(first, left_index)] * inverse[(second, right_index)] * bach_action[(left_index, right_index)]
                for left_index, right_index in product(range(DIMENSION), repeat=2)
            ),
            order=0,
        )
    return metric, output


def bach_euler_density_coefficient(
    left: MetricJets,
    right: MetricJets,
    a_degree: int,
    b_degree: int,
    *,
    background: Mapping[tuple[int, int], Jet] | None = None,
) -> dict[tuple[int, int], Fraction]:
    """Evaluate a selected square-free parameter coefficient of ``E^munu``."""

    _, density = _bach_euler_density_jets(left, right, background=background)
    return {pair: density[pair].coefficient(a_degree, b_degree) for pair in PAIRS}


def polarized_bach_euler_density(
    left: MetricJets,
    right: MetricJets,
    *,
    background: Mapping[tuple[int, int], Jet] | None = None,
) -> dict[tuple[int, int], Fraction]:
    """Evaluate ``coeff_ab E^munu(gbar+a h1+b h2)`` exactly at the chart base point."""

    return bach_euler_density_coefficient(left, right, 1, 1, background=background)


def polarized_weyl_trace_identity(
    left: MetricJets,
    right: MetricJets,
    *,
    background: Mapping[tuple[int, int], Jet] | None = None,
) -> Fraction:
    """Return the ``a*b`` coefficient of the exact identity ``g_ab E^ab=0``."""

    metric, density = _bach_euler_density_jets(left, right, background=background)
    trace = sum_jets((metric[(a, b)] * density[(a, b)] for a, b in product(range(DIMENSION), repeat=2)), order=0)
    return trace.coefficient(1, 1)


def cylinder_background_invariants() -> dict[str, object]:
    """Exact base-point checks for the unperturbed unit conformal cylinder."""

    geometry = _geometry(cylinder_background())
    ricci = geometry["ricci"]
    scalar = geometry["scalar"]
    assert isinstance(ricci, Mapping) and isinstance(scalar, Jet)
    _, weyl = _schouten_and_weyl(geometry)
    bach = _bach_lower(geometry)
    return {
        "ricci_lower": [[str(ricci[(a, b)].constant_term) for b in range(DIMENSION)] for a in range(DIMENSION)],
        "scalar": str(scalar.constant_term),
        "weyl_background_nonzero_components": sum(value.constant_term != 0 for value in weyl.values()),
        "bach_background_nonzero_components": sum(value.constant_term != 0 for value in bach.values()),
    }


def ppwave_profile_fixture(seed: int) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    """An exact polynomial ``H(u,x,y) du^2`` jet, independent of ``v``."""

    words = (ZERO_MULTIINDEX, (1, 0, 0, 0), (0, 0, 2, 0), (1, 0, 1, 1), (0, 0, 0, 4))
    return {
        (0, 0): {
            word: Fraction((seed + index * 3) % 11 - 5, index % 3 + 1)
            for index, word in enumerate(words)
        }
    }


def conformal_metric_fixture(coefficients: CoordinateJet) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    """Return the exact infinitesimal Weyl direction ``h_ab=2 omega gbar_ab``."""

    omega = Jet.coordinate_series(4, coefficients)
    background = cylinder_background()
    output = {}
    for pair in PAIRS:
        value = (background[pair] * omega).scale(2)
        output[pair] = {alpha: coefficient for a, b, alpha, coefficient in value.terms if a == b == 0}
    return output


def sparse_fixture(seed: int) -> dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]]:
    """Deterministic, non-special exact input used only by prototype smoke tests."""

    output: dict[tuple[int, int], dict[tuple[int, int, int, int], Fraction]] = {}
    words = (ZERO_MULTIINDEX, (1, 0, 0, 0), (0, 1, 1, 0), (0, 0, 0, 4))
    for index, pair in enumerate(PAIRS):
        selected = words[(index + seed) % len(words)]
        output[pair] = {selected: Fraction((index + 2 * seed) % 7 - 3, index % 3 + 1)}
    return output


def swap_fixture_result(left: MetricJets, right: MetricJets) -> bool:
    return polarized_bach_euler_density(left, right) == polarized_bach_euler_density(right, left)


if __name__ == "__main__":
    first, second = sparse_fixture(1), sparse_fixture(2)
    result = polarized_bach_euler_density(first, second)
    print("STRICT_CYLINDER_POLARIZED_BACH_EVALUATOR_SMOKE")
    print("swap_symmetric", result == polarized_bach_euler_density(second, first))
    print("nonzero_outputs", sum(value != 0 for value in result.values()))
    for pair, value in result.items():
        print(pair, value)
