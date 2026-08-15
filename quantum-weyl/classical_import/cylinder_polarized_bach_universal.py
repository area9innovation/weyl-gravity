#!/usr/bin/env python3
"""Universal exact local-operator AD for the cylinder Bach Hessian.

Unlike :mod:`cylinder_polarized_bach_evaluator`, which evaluates two supplied
rational four-jets, this module propagates the complete linear and bilinear
metric-jet operators through the natural geometric construction.  Coefficient
functions are exact rational coordinate jets about the homogeneous cylinder
point.  Bilinear slots remain ordered until an explicit symmetry audit.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, permutations, product
from math import isqrt
from typing import Iterable, Mapping, Sequence


DIMENSION = 4
ZERO_WORD = (0,) * DIMENSION
PAIRS = tuple((a, b) for a in range(DIMENSION) for b in range(a, DIMENSION))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
InputKey = tuple[int, tuple[int, int, int, int]]
BilinearKey = tuple[int, tuple[int, int, int, int], int, tuple[int, int, int, int]]


def _q(value: Fraction | int) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(value)


def _degree(word: Sequence[int]) -> int:
    return sum(word)


def _increment(word: tuple[int, int, int, int], axis: int) -> tuple[int, int, int, int]:
    value = list(word)
    value[axis] += 1
    return tuple(value)


@dataclass(frozen=True)
class CoefficientJet:
    """Normalized exact coordinate Taylor coefficients through a fixed order."""

    order: int
    terms: tuple[tuple[tuple[int, int, int, int], Fraction], ...] = ()

    @staticmethod
    def from_terms(order: int, terms: Iterable[tuple[Sequence[int], Fraction | int]]) -> "CoefficientJet":
        if order < 0:
            return CoefficientJet(-1)
        combined: dict[tuple[int, int, int, int], Fraction] = {}
        for word, coefficient in terms:
            word = tuple(int(item) for item in word)
            if len(word) != DIMENSION or min(word) < 0:
                raise ValueError("coefficient word must contain four nonnegative entries")
            coefficient = _q(coefficient)
            if coefficient and _degree(word) <= order:
                combined[word] = combined.get(word, Fraction(0)) + coefficient
        return CoefficientJet(order, tuple((word, value) for word, value in sorted(combined.items()) if value))

    @staticmethod
    def zero(order: int) -> "CoefficientJet":
        return CoefficientJet(order)

    @staticmethod
    def constant(order: int, value: Fraction | int) -> "CoefficientJet":
        return CoefficientJet.from_terms(order, ((ZERO_WORD, value),))

    @property
    def base(self) -> Fraction:
        return next((value for word, value in self.terms if word == ZERO_WORD), Fraction(0))

    def truncate(self, order: int) -> "CoefficientJet":
        return CoefficientJet.from_terms(min(order, self.order), self.terms)

    def __add__(self, other: "CoefficientJet") -> "CoefficientJet":
        order = min(self.order, other.order)
        return CoefficientJet.from_terms(order, (*self.truncate(order).terms, *other.truncate(order).terms))

    def __neg__(self) -> "CoefficientJet":
        return CoefficientJet.from_terms(self.order, ((word, -value) for word, value in self.terms))

    def __sub__(self, other: "CoefficientJet") -> "CoefficientJet":
        return self + (-other)

    def scale(self, value: Fraction | int) -> "CoefficientJet":
        value = _q(value)
        return CoefficientJet.from_terms(self.order, ((word, value * coefficient) for word, coefficient in self.terms))

    def __mul__(self, other: "CoefficientJet") -> "CoefficientJet":
        order = min(self.order, other.order)
        return CoefficientJet.from_terms(
            order,
            (
                (tuple(left[index] + right[index] for index in range(DIMENSION)), first * second)
                for left, first in self.terms
                for right, second in other.terms
            ),
        )

    def derivative(self, axis: int) -> "CoefficientJet":
        if self.order <= 0:
            return CoefficientJet.zero(self.order - 1)
        return CoefficientJet.from_terms(
            self.order - 1,
            (
                (tuple(item - (index == axis) for index, item in enumerate(word)), word[axis] * value)
                for word, value in self.terms
                if word[axis]
            ),
        )

    def reciprocal(self) -> "CoefficientJet":
        if not self.base:
            raise ZeroDivisionError("coefficient series has no invertible base value")
        one = CoefficientJet.constant(self.order, 1)
        reduced = self.scale(Fraction(1, self.base)) - one
        output = one
        power = one
        for exponent in range(1, self.order + 1):
            power = power * reduced
            output = output + power.scale(-1 if exponent % 2 else 1)
        return output.scale(Fraction(1, self.base))

    def sqrt(self) -> "CoefficientJet":
        numerator = isqrt(self.base.numerator)
        denominator = isqrt(self.base.denominator)
        if numerator * numerator != self.base.numerator or denominator * denominator != self.base.denominator:
            raise ValueError("coefficient square root requires a rational-square base")
        root = Fraction(numerator, denominator)
        one = CoefficientJet.constant(self.order, 1)
        reduced = self.scale(Fraction(1, self.base)) - one
        output = one
        power = one
        coefficient = Fraction(1)
        for exponent in range(1, self.order + 1):
            power = power * reduced
            coefficient *= Fraction(3 - 2 * exponent, 2 * exponent)
            output = output + power.scale(coefficient)
        return output.scale(root)


@dataclass(frozen=True)
class LinearOperator:
    order: int
    terms: tuple[tuple[int, tuple[int, int, int, int], CoefficientJet], ...] = ()

    @staticmethod
    def from_terms(order: int, terms: Iterable[tuple[int, Sequence[int], CoefficientJet]]) -> "LinearOperator":
        if order < 0:
            return LinearOperator(-1)
        combined: dict[InputKey, CoefficientJet] = {}
        for component, word, coefficient in terms:
            word = tuple(int(item) for item in word)
            coefficient = coefficient.truncate(order)
            if coefficient.terms:
                key = (int(component), word)
                combined[key] = combined.get(key, CoefficientJet.zero(order)) + coefficient
        return LinearOperator(order, tuple((*key, value) for key, value in sorted(combined.items()) if value.terms))

    @staticmethod
    def zero(order: int) -> "LinearOperator":
        return LinearOperator(order)

    @staticmethod
    def basis(order: int, component: int) -> "LinearOperator":
        return LinearOperator(order, ((component, ZERO_WORD, CoefficientJet.constant(order, 1)),))

    def truncate(self, order: int) -> "LinearOperator":
        return LinearOperator.from_terms(min(order, self.order), self.terms)

    def __add__(self, other: "LinearOperator") -> "LinearOperator":
        order = min(self.order, other.order)
        return LinearOperator.from_terms(order, (*self.truncate(order).terms, *other.truncate(order).terms))

    def __neg__(self) -> "LinearOperator":
        return LinearOperator.from_terms(self.order, ((component, word, -coefficient) for component, word, coefficient in self.terms))

    def __sub__(self, other: "LinearOperator") -> "LinearOperator":
        return self + (-other)

    def scale(self, coefficient: CoefficientJet | Fraction | int) -> "LinearOperator":
        if not isinstance(coefficient, CoefficientJet):
            coefficient = CoefficientJet.constant(self.order, coefficient)
        order = min(self.order, coefficient.order)
        return LinearOperator.from_terms(order, ((component, word, value * coefficient) for component, word, value in self.terms))

    def derivative(self, axis: int) -> "LinearOperator":
        if self.order <= 0:
            return LinearOperator.zero(self.order - 1)
        return LinearOperator.from_terms(
            self.order - 1,
            (
                term
                for component, word, coefficient in self.terms
                for term in (
                    (component, word, coefficient.derivative(axis)),
                    (component, _increment(word, axis), coefficient.truncate(self.order - 1).scale(word[axis] + 1)),
                )
            ),
        )


@dataclass(frozen=True)
class BilinearOperator:
    order: int
    terms: tuple[tuple[int, tuple[int, int, int, int], int, tuple[int, int, int, int], CoefficientJet], ...] = ()

    @staticmethod
    def from_terms(order: int, terms: Iterable[tuple[int, Sequence[int], int, Sequence[int], CoefficientJet]]) -> "BilinearOperator":
        if order < 0:
            return BilinearOperator(-1)
        combined: dict[BilinearKey, CoefficientJet] = {}
        for left, left_word, right, right_word, coefficient in terms:
            left_word, right_word = tuple(left_word), tuple(right_word)
            coefficient = coefficient.truncate(order)
            if coefficient.terms:
                key = (int(left), left_word, int(right), right_word)
                combined[key] = combined.get(key, CoefficientJet.zero(order)) + coefficient
        return BilinearOperator(order, tuple((*key, value) for key, value in sorted(combined.items()) if value.terms))

    @staticmethod
    def zero(order: int) -> "BilinearOperator":
        return BilinearOperator(order)

    def truncate(self, order: int) -> "BilinearOperator":
        return BilinearOperator.from_terms(min(order, self.order), self.terms)

    def __add__(self, other: "BilinearOperator") -> "BilinearOperator":
        order = min(self.order, other.order)
        return BilinearOperator.from_terms(order, (*self.truncate(order).terms, *other.truncate(order).terms))

    def __neg__(self) -> "BilinearOperator":
        return BilinearOperator.from_terms(self.order, ((left, lw, right, rw, -coefficient) for left, lw, right, rw, coefficient in self.terms))

    def __sub__(self, other: "BilinearOperator") -> "BilinearOperator":
        return self + (-other)

    def scale(self, coefficient: CoefficientJet | Fraction | int) -> "BilinearOperator":
        if not isinstance(coefficient, CoefficientJet):
            coefficient = CoefficientJet.constant(self.order, coefficient)
        order = min(self.order, coefficient.order)
        return BilinearOperator.from_terms(order, ((left, lw, right, rw, value * coefficient) for left, lw, right, rw, value in self.terms))

    def derivative(self, axis: int) -> "BilinearOperator":
        if self.order <= 0:
            return BilinearOperator.zero(self.order - 1)
        return BilinearOperator.from_terms(
            self.order - 1,
            (
                term
                for left, lw, right, rw, coefficient in self.terms
                for term in (
                    (left, lw, right, rw, coefficient.derivative(axis)),
                    (left, _increment(lw, axis), right, rw, coefficient.truncate(self.order - 1).scale(lw[axis] + 1)),
                    (left, lw, right, _increment(rw, axis), coefficient.truncate(self.order - 1).scale(rw[axis] + 1)),
                )
            ),
        )

    def at_base(self) -> dict[BilinearKey, Fraction]:
        return {(left, lw, right, rw): coefficient.base for left, lw, right, rw, coefficient in self.terms if coefficient.base}


def _outer(first: LinearOperator, second: LinearOperator) -> BilinearOperator:
    order = min(first.order, second.order)
    return BilinearOperator.from_terms(
        order,
        (
            (left, lw, right, rw, left_value * right_value)
            for left, lw, left_value in first.terms
            for right, rw, right_value in second.terms
        ),
    )


@dataclass(frozen=True)
class NaturalTaylor:
    order: int
    background: CoefficientJet
    linear: LinearOperator
    bilinear: BilinearOperator

    @staticmethod
    def constant(order: int, value: CoefficientJet | Fraction | int) -> "NaturalTaylor":
        background = value.truncate(order) if isinstance(value, CoefficientJet) else CoefficientJet.constant(order, value)
        return NaturalTaylor(order, background, LinearOperator.zero(order), BilinearOperator.zero(order))

    @staticmethod
    def field(order: int, component: int, background: CoefficientJet) -> "NaturalTaylor":
        return NaturalTaylor(order, background.truncate(order), LinearOperator.basis(order, component), BilinearOperator.zero(order))

    def truncate(self, order: int) -> "NaturalTaylor":
        order = min(order, self.order)
        return NaturalTaylor(order, self.background.truncate(order), self.linear.truncate(order), self.bilinear.truncate(order))

    def __add__(self, other: "NaturalTaylor") -> "NaturalTaylor":
        order = min(self.order, other.order)
        first, second = self.truncate(order), other.truncate(order)
        return NaturalTaylor(order, first.background + second.background, first.linear + second.linear, first.bilinear + second.bilinear)

    def __neg__(self) -> "NaturalTaylor":
        return NaturalTaylor(self.order, -self.background, -self.linear, -self.bilinear)

    def __sub__(self, other: "NaturalTaylor") -> "NaturalTaylor":
        return self + (-other)

    def scale(self, value: CoefficientJet | Fraction | int) -> "NaturalTaylor":
        coefficient = value if isinstance(value, CoefficientJet) else CoefficientJet.constant(self.order, value)
        order = min(self.order, coefficient.order)
        current = self.truncate(order)
        coefficient = coefficient.truncate(order)
        return NaturalTaylor(order, current.background * coefficient, current.linear.scale(coefficient), current.bilinear.scale(coefficient))

    def __mul__(self, other: "NaturalTaylor") -> "NaturalTaylor":
        order = min(self.order, other.order)
        first, second = self.truncate(order), other.truncate(order)
        return NaturalTaylor(
            order,
            first.background * second.background,
            first.linear.scale(second.background) + second.linear.scale(first.background),
            first.bilinear.scale(second.background)
            + second.bilinear.scale(first.background)
            + _outer(first.linear, second.linear)
            + _outer(second.linear, first.linear),
        )

    def derivative(self, axis: int) -> "NaturalTaylor":
        return NaturalTaylor(self.order - 1, self.background.derivative(axis), self.linear.derivative(axis), self.bilinear.derivative(axis))

    def reciprocal(self) -> "NaturalTaylor":
        inverse = self.background.reciprocal()
        inverse2 = inverse * inverse
        return NaturalTaylor(
            self.order,
            inverse,
            self.linear.scale(-inverse2),
            self.bilinear.scale(-inverse2) + _outer(self.linear, self.linear).scale((inverse2 * inverse).scale(2)),
        )

    def sqrt(self) -> "NaturalTaylor":
        root = self.background.sqrt()
        first = root.reciprocal().scale(Fraction(1, 2))
        second = (root * root * root).reciprocal().scale(Fraction(-1, 4))
        return NaturalTaylor(
            self.order,
            root,
            self.linear.scale(first),
            self.bilinear.scale(first) + _outer(self.linear, self.linear).scale(second),
        )


def sum_natural(values: Iterable[NaturalTaylor], order: int | None = None) -> NaturalTaylor:
    values = tuple(values)
    if not values:
        if order is None:
            raise ValueError("empty natural sum requires an order")
        return NaturalTaylor.constant(order, 0)
    target = min(value.order for value in values) if order is None else min(order, *(value.order for value in values))
    values = tuple(value.truncate(target) for value in values)
    return NaturalTaylor(
        target,
        CoefficientJet.from_terms(target, (term for value in values for term in value.background.terms)),
        LinearOperator.from_terms(target, (term for value in values for term in value.linear.terms)),
        BilinearOperator.from_terms(target, (term for value in values for term in value.bilinear.terms)),
    )


def _cos_squared(order: int, axis: int) -> CoefficientJet:
    words = [list(ZERO_WORD) for _ in range(3)]
    words[1][axis], words[2][axis] = 2, 4
    return CoefficientJet.from_terms(order, ((words[0], 1), (words[1], -1), (words[2], Fraction(1, 3))))


def metric_jet(order: int = 4) -> dict[tuple[int, int], NaturalTaylor]:
    cos2_x, cos2_y = _cos_squared(order, 1), _cos_squared(order, 2)
    diagonal = {
        0: CoefficientJet.constant(order, -1),
        1: CoefficientJet.constant(order, 1),
        2: cos2_x,
        3: cos2_x * cos2_y,
    }
    return {
        (a, b): NaturalTaylor.field(order, PAIR_INDEX[tuple(sorted((a, b)))], diagonal[a] if a == b else CoefficientJet.zero(order))
        for a, b in product(range(DIMENSION), repeat=2)
    }


def inverse_metric(metric: Mapping[tuple[int, int], NaturalTaylor]) -> dict[tuple[int, int], NaturalTaylor]:
    order = min(value.order for value in metric.values())
    backgrounds = {pair: metric[pair].background for pair in metric}
    inverse_background = {(a, b): CoefficientJet.zero(order) for a, b in product(range(DIMENSION), repeat=2)}
    for index in range(DIMENSION):
        inverse_background[(index, index)] = backgrounds[(index, index)].reciprocal()
    output = {}
    for a, b in product(range(DIMENSION), repeat=2):
        linear = LinearOperator.zero(order)
        bilinear = BilinearOperator.zero(order)
        for i, j in product(range(DIMENSION), repeat=2):
            coefficient = inverse_background[(a, i)] * inverse_background[(j, b)]
            if coefficient.terms:
                linear = linear + metric[(i, j)].linear.scale(-coefficient)
        for i, j, k, l in product(range(DIMENSION), repeat=4):
            coefficient = inverse_background[(a, i)] * inverse_background[(j, k)] * inverse_background[(l, b)]
            if coefficient.terms:
                bilinear = bilinear + (
                    _outer(metric[(i, j)].linear, metric[(k, l)].linear)
                    + _outer(metric[(k, l)].linear, metric[(i, j)].linear)
                ).scale(coefficient)
        output[(a, b)] = NaturalTaylor(order, inverse_background[(a, b)], linear, bilinear)
    return output


def determinant(metric: Mapping[tuple[int, int], NaturalTaylor]) -> NaturalTaylor:
    order = min(value.order for value in metric.values())
    terms = []
    for permutation in permutations(range(DIMENSION)):
        inversions = sum(permutation[a] > permutation[b] for a in range(DIMENSION) for b in range(a + 1, DIMENSION))
        value = NaturalTaylor.constant(order, -1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            value = value * metric[(row, column)]
        terms.append(value)
    return sum_natural(terms)


def _connection(metric: Mapping[tuple[int, int], NaturalTaylor], inverse: Mapping[tuple[int, int], NaturalTaylor]) -> dict[tuple[int, int, int], NaturalTaylor]:
    connection_order = min(value.order for value in metric.values()) - 1
    return {
        (target, left, right): sum_natural(
            (
                inverse[(target, index)]
                * (
                    metric[(index, right)].derivative(left)
                    + metric[(index, left)].derivative(right)
                    - metric[(left, right)].derivative(index)
                ).scale(Fraction(1, 2))
                for index in range(DIMENSION)
            ),
            order=connection_order,
        )
        for target, left, right in product(range(DIMENSION), repeat=3)
    }


def _geometry(metric: Mapping[tuple[int, int], NaturalTaylor]) -> dict[str, object]:
    curvature_order = min(value.order for value in metric.values()) - 2
    inverse = inverse_metric(metric)
    gamma = _connection(metric, inverse)
    riemann = {
        (target, vector, first, second): (
            gamma[(target, second, vector)].derivative(first)
            - gamma[(target, first, vector)].derivative(second)
            + sum_natural(
                (
                    gamma[(middle, second, vector)] * gamma[(target, first, middle)]
                    - gamma[(middle, first, vector)] * gamma[(target, second, middle)]
                    for middle in range(DIMENSION)
                ),
                order=curvature_order,
            )
        ).truncate(curvature_order)
        for target, vector, first, second in product(range(DIMENSION), repeat=4)
    }
    ricci = {(a, b): sum_natural((riemann[(index, a, index, b)] for index in range(DIMENSION)), order=curvature_order) for a, b in product(range(DIMENSION), repeat=2)}
    scalar = sum_natural((inverse[(a, b)] * ricci[(a, b)] for a, b in product(range(DIMENSION), repeat=2)), order=curvature_order)
    return {"metric": metric, "inverse": inverse, "connection": gamma, "riemann": riemann, "ricci": ricci, "scalar": scalar}


def _schouten_and_weyl(geometry: Mapping[str, object]) -> tuple[dict[tuple[int, int], NaturalTaylor], dict[tuple[int, int, int, int], NaturalTaylor]]:
    metric, riemann, ricci, scalar = geometry["metric"], geometry["riemann"], geometry["ricci"], geometry["scalar"]
    assert isinstance(metric, Mapping) and isinstance(riemann, Mapping) and isinstance(ricci, Mapping) and isinstance(scalar, NaturalTaylor)
    curvature_order = scalar.order
    schouten = {}
    for a, b in PAIRS:
        value = (ricci[(a, b)] - metric[(a, b)] * scalar.scale(Fraction(1, 6))).scale(Fraction(1, 2)).truncate(curvature_order)
        schouten[(a, b)] = schouten[(b, a)] = value
    two_forms = tuple(combinations(range(DIMENSION), 2))
    canonical_weyl = {}
    for left_index, (a, b) in enumerate(two_forms):
        for c, d in two_forms[left_index:]:
            lowered = sum_natural((metric[(a, target)] * riemann[(target, b, c, d)] for target in range(DIMENSION)), order=curvature_order)
            correction = metric[(a, c)] * schouten[(d, b)] - metric[(a, d)] * schouten[(c, b)] - metric[(b, c)] * schouten[(d, a)] + metric[(b, d)] * schouten[(c, a)]
            canonical_weyl[((a, b), (c, d))] = (lowered - correction).truncate(2)
    zero = NaturalTaylor.constant(curvature_order, 0)
    weyl = {}
    for a, b, c, d in product(range(DIMENSION), repeat=4):
        if a == b or c == d:
            weyl[(a, b, c, d)] = zero
            continue
        left, right = tuple(sorted((a, b))), tuple(sorted((c, d)))
        sign = (1 if a < b else -1) * (1 if c < d else -1)
        value = canonical_weyl[(left, right)] if left <= right else canonical_weyl[(right, left)]
        weyl[(a, b, c, d)] = value.scale(sign)
    return schouten, weyl


def _bach_lower(geometry: Mapping[str, object]) -> dict[tuple[int, int], NaturalTaylor]:
    inverse, gamma = geometry["inverse"], geometry["connection"]
    assert isinstance(inverse, Mapping) and isinstance(gamma, Mapping)
    schouten, weyl = _schouten_and_weyl(geometry)
    curvature_order = next(iter(schouten.values())).order
    cotton_order = curvature_order - 1
    bach_order = cotton_order - 1
    first_schouten = {}
    for axis in range(DIMENSION):
        for first, second in PAIRS:
            value = (
                schouten[(first, second)].derivative(axis)
                - sum_natural(
                    (
                        gamma[(replacement, axis, first)] * schouten[(replacement, second)]
                        + gamma[(replacement, axis, second)] * schouten[(first, replacement)]
                        for replacement in range(DIMENSION)
                    ),
                    order=cotton_order,
                )
            ).truncate(cotton_order)
            first_schouten[(axis, first, second)] = first_schouten[(axis, second, first)] = value
    cotton = {}
    zero = NaturalTaylor.constant(cotton_order, 0)
    for second in range(DIMENSION):
        for inner in range(DIMENSION):
            cotton[(inner, inner, second)] = zero
        for inner, first in combinations(range(DIMENSION), 2):
            value = first_schouten[(inner, first, second)] - first_schouten[(first, second, inner)]
            cotton[(inner, first, second)] = value
            cotton[(first, inner, second)] = -value
    divergence = {}
    for first, second in PAIRS:
        contracted = []
        for outer, inner in product(range(DIMENSION), repeat=2):
            derivative = cotton[(inner, first, second)].derivative(outer) - sum_natural(
                (
                    gamma[(replacement, outer, inner)] * cotton[(replacement, first, second)]
                    + gamma[(replacement, outer, first)] * cotton[(inner, replacement, second)]
                    + gamma[(replacement, outer, second)] * cotton[(inner, first, replacement)]
                    for replacement in range(DIMENSION)
                ),
                order=bach_order,
            )
            contracted.append(inverse[(outer, inner)] * derivative)
        value = sum_natural(contracted, order=bach_order)
        divergence[(first, second)] = divergence[(second, first)] = value
    schouten_up = {}
    for first, second in PAIRS:
        value = sum_natural(
            (inverse[(first, left)] * inverse[(second, right)] * schouten[(left, right)] for left, right in product(range(DIMENSION), repeat=2)),
            order=bach_order,
        )
        schouten_up[(first, second)] = schouten_up[(second, first)] = value
    algebraic = {}
    for first, second in PAIRS:
        value = sum_natural((schouten_up[(inner, outer)] * weyl[(first, inner, second, outer)] for inner, outer in product(range(DIMENSION), repeat=2)), order=bach_order)
        algebraic[(first, second)] = algebraic[(second, first)] = value
    output = {}
    for first, second in PAIRS:
        value = (divergence[(first, second)] + algebraic[(first, second)]).truncate(bach_order)
        output[(first, second)] = output[(second, first)] = value
    return output


def universal_euler_construction(output_coordinate_order: int = 0) -> dict[str, object]:
    """Construct exact Euler-density Taylor rows through a coordinate order."""

    if output_coordinate_order < 0:
        raise ValueError("output coordinate order must be nonnegative")
    metric = metric_jet(4 + output_coordinate_order)
    geometry = _geometry(metric)
    inverse = geometry["inverse"]
    assert isinstance(inverse, Mapping)
    bach_action = {pair: value.scale(-2) for pair, value in _bach_lower(geometry).items()}
    volume = determinant(metric).scale(-1).sqrt().truncate(output_coordinate_order)
    density_rows = {}
    for first, second in PAIRS:
        density = volume * sum_natural(
            (inverse[(first, left)] * inverse[(second, right)] * bach_action[(left, right)] for left, right in product(range(DIMENSION), repeat=2)),
            order=output_coordinate_order,
        )
        density_rows[(first, second)] = density_rows[(second, first)] = density
    return {"metric": metric, "density_rows": density_rows, "output_coordinate_order": output_coordinate_order}


def universal_euler_rows(construction: Mapping[str, object] | None = None) -> dict[tuple[int, int], BilinearOperator]:
    """Return all ten exact ordered-slot Bach-Hessian operators at the base point."""

    construction = universal_euler_construction() if construction is None else construction
    density_rows = construction["density_rows"]
    assert isinstance(density_rows, Mapping)
    return {pair: density_rows[pair].bilinear for pair in PAIRS}


def universal_weyl_trace_defects(construction: Mapping[str, object]) -> dict[str, object]:
    """Replay ``g_ab E^ab=0`` through quadratic order on the universal operators."""

    metric, density_rows = construction["metric"], construction["density_rows"]
    assert isinstance(metric, Mapping) and isinstance(density_rows, Mapping)
    trace = sum_natural((metric[(a, b)] * density_rows[(a, b)] for a, b in product(range(DIMENSION), repeat=2)), order=0)
    return {
        "background": str(trace.background.base),
        "linear_term_count": len(trace.linear.terms),
        "bilinear_term_count": len(trace.bilinear.at_base()),
    }


def universal_diff_noether_defects(construction: Mapping[str, object]) -> dict[str, object]:
    """Replay the Diff identity through quadratic order at the base point.

    For a symmetric contravariant Euler density the coordinate identity is

    ``E^ab partial_lambda g_ab - 2 partial_a(E^ab g_lambda_b)=0``.

    Its derivative raises the required metric-jet order from four to five, so
    the construction must retain at least one output coordinate derivative.
    """

    if construction.get("output_coordinate_order", 0) < 1:
        raise ValueError("Diff Noether replay requires output coordinate order at least one")
    metric, density_rows = construction["metric"], construction["density_rows"]
    assert isinstance(metric, Mapping) and isinstance(density_rows, Mapping)
    rows = []
    for covector in range(DIMENSION):
        metric_derivative = sum_natural(
            (density_rows[(a, b)] * metric[(a, b)].derivative(covector) for a, b in product(range(DIMENSION), repeat=2)),
            order=0,
        )
        product_divergence = sum_natural(
            (
                (density_rows[(a, b)] * metric[(covector, b)]).derivative(a)
                for a, b in product(range(DIMENSION), repeat=2)
            ),
            order=0,
        )
        rows.append(metric_derivative - product_divergence.scale(2))
    return {
        "coordinate_formula": "E^ab partial_lambda g_ab - 2 partial_a(E^ab g_lambda_b)=0",
        "required_metric_jet_order": 5,
        "rows": [
            {
                "covector_index": index,
                "background": str(row.background.base),
                "linear_term_count": len(row.linear.terms),
                "bilinear_term_count": len(row.bilinear.at_base()),
            }
            for index, row in enumerate(rows)
        ],
    }


def symmetry_defects(rows: Mapping[tuple[int, int], BilinearOperator]) -> list[tuple[tuple[int, int], BilinearKey, Fraction, Fraction]]:
    defects = []
    for output, operator in rows.items():
        terms = operator.at_base()
        keys = set(terms) | {(right, rw, left, lw) for left, lw, right, rw in terms}
        for key in sorted(keys):
            left, lw, right, rw = key
            swapped = (right, rw, left, lw)
            if terms.get(key, Fraction(0)) != terms.get(swapped, Fraction(0)) and key <= swapped:
                defects.append((output, key, terms.get(key, Fraction(0)), terms.get(swapped, Fraction(0))))
    return defects


def evaluate_rows(rows: Mapping[tuple[int, int], BilinearOperator], left: Mapping[tuple[int, int], Mapping[tuple[int, int, int, int], Fraction]], right: Mapping[tuple[int, int], Mapping[tuple[int, int, int, int], Fraction]]) -> dict[tuple[int, int], Fraction]:
    """Apply the universal table to concrete normalized input jets."""

    def coefficient(values: Mapping[tuple[int, int], Mapping[tuple[int, int, int, int], Fraction]], component: int, word: tuple[int, int, int, int]) -> Fraction:
        return _q(values.get(PAIRS[component], {}).get(word, 0))

    return {
        output: sum(
            value * coefficient(left, left_component, left_word) * coefficient(right, right_component, right_word)
            for (left_component, left_word, right_component, right_word), value in operator.at_base().items()
        )
        for output, operator in rows.items()
    }


if __name__ == "__main__":
    construction = universal_euler_construction()
    rows = universal_euler_rows(construction)
    print("STRICT_CYLINDER_POLARIZED_BACH_UNIVERSAL")
    print("term_counts", {str(pair): len(operator.at_base()) for pair, operator in rows.items()})
    print("symmetry_defects", len(symmetry_defects(rows)))
    print("weyl_trace_defects", universal_weyl_trace_defects(construction))
