"""Exact equatorial coefficient-jet engine for the compact product.

This is intentionally narrow.  Coefficients on the homogeneous
``R x S1 x S2`` background depend only on ``theta``.  Storing their finite
Taylor jets at ``theta=pi/2`` avoids the expression swell caused by repeatedly
differentiating large trigonometric PBW coefficients.  It is not a general
polydifferential coefficient engine.

``ThetaJet.values[n]`` is the exact n-th theta derivative at the equator.
The polarized field Taylor convention is unchanged: bilinear and trilinear
operators carry derivatives with no factorial absorbed.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations_with_replacement, permutations, product
from math import comb
from typing import Iterable, Sequence

import sympy as sp


COEFFICIENT_JET_ORDER = 10
COORDINATE_COUNT = 4
THETA_AXIS = 2
PAIRS = tuple((a, b) for a in range(4) for b in range(a, 4))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}


@dataclass(frozen=True)
class ThetaJet:
    values: tuple[sp.Rational, ...]
    valid_through: int = COEFFICIENT_JET_ORDER

    def __post_init__(self) -> None:
        if len(self.values) != COEFFICIENT_JET_ORDER + 1:
            raise ValueError("coefficient jet storage length drifted")
        if not 0 <= self.valid_through <= COEFFICIENT_JET_ORDER:
            raise ValueError("invalid authoritative coefficient-jet depth")

    @staticmethod
    def constant(value: object) -> "ThetaJet":
        rational = sp.Rational(value)
        return ThetaJet((rational,) + (sp.S.Zero,) * COEFFICIENT_JET_ORDER)

    @staticmethod
    def from_derivatives(values: Sequence[object]) -> "ThetaJet":
        padded = tuple(sp.Rational(value) for value in values)
        if not padded:
            raise ValueError("coefficient jet requires a base value")
        if len(padded) > COEFFICIENT_JET_ORDER + 1:
            raise ValueError("too many coefficient derivatives")
        return ThetaJet(
            padded + (sp.S.Zero,) * (COEFFICIENT_JET_ORDER + 1 - len(padded)),
            len(padded) - 1,
        )

    @staticmethod
    def sin_equator() -> "ThetaJet":
        return ThetaJet.from_derivatives(
            sp.Integer(0) if order % 2 else sp.Integer(-1) ** (order // 2)
            for order in range(COEFFICIENT_JET_ORDER + 1)
        )

    @staticmethod
    def cos_equator() -> "ThetaJet":
        return ThetaJet.from_derivatives(
            sp.Integer(0) if order % 2 == 0 else sp.Integer(-1) ** ((order - 1) // 2 + 1)
            for order in range(COEFFICIENT_JET_ORDER + 1)
        )

    def __add__(self, other: object) -> "ThetaJet":
        other = as_theta(other)
        valid = min(self.valid_through, other.valid_through)
        return ThetaJet(
            tuple(
                self.values[order] + other.values[order]
                if order <= valid
                else sp.S.Zero
                for order in range(COEFFICIENT_JET_ORDER + 1)
            ),
            valid,
        )

    def __radd__(self, other: object) -> "ThetaJet":
        return self + other

    def __neg__(self) -> "ThetaJet":
        return ThetaJet(
            tuple(
                -self.values[order] if order <= self.valid_through else sp.S.Zero
                for order in range(COEFFICIENT_JET_ORDER + 1)
            ),
            self.valid_through,
        )

    def __sub__(self, other: object) -> "ThetaJet":
        return self + (-as_theta(other))

    def __rsub__(self, other: object) -> "ThetaJet":
        return as_theta(other) - self

    def __mul__(self, other: object) -> "ThetaJet":
        other = as_theta(other)
        if self.is_zero or other.is_zero:
            return ZERO
        valid = min(self.valid_through, other.valid_through)
        return ThetaJet(
            tuple(
                sum(
                    (
                        sp.Integer(comb(order, left))
                        * self.values[left]
                        * other.values[order - left]
                        for left in range(order + 1)
                    ),
                    sp.S.Zero,
                )
                if order <= valid
                else sp.S.Zero
                for order in range(COEFFICIENT_JET_ORDER + 1)
            ),
            valid,
        )

    def __rmul__(self, other: object) -> "ThetaJet":
        return self * other

    def reciprocal(self) -> "ThetaJet":
        if self.values[0] == 0:
            raise ZeroDivisionError("coefficient jet has zero base value")
        output = [sp.S.One / self.values[0]]
        for order in range(1, self.valid_through + 1):
            value = -sum(
                sp.Integer(comb(order, left)) * self.values[left] * output[order - left]
                for left in range(1, order + 1)
            ) / self.values[0]
            output.append(sp.cancel(value))
        return ThetaJet(
            tuple(output) + (sp.S.Zero,) * (COEFFICIENT_JET_ORDER + 1 - len(output)),
            self.valid_through,
        )

    def __truediv__(self, other: object) -> "ThetaJet":
        return self * as_theta(other).reciprocal()

    def power(self, exponent: int) -> "ThetaJet":
        if exponent < 0:
            return self.reciprocal().power(-exponent)
        output = ONE
        for _ in range(exponent):
            output = output * self
        return output

    def sqrt(self) -> "ThetaJet":
        root = sp.sqrt(self.values[0])
        if not root.is_Rational:
            raise ValueError(f"coefficient square root escaped Q: {root}")
        output = [sp.Rational(root)]
        for order in range(1, self.valid_through + 1):
            middle = sum(
                sp.Integer(comb(order, left)) * output[left] * output[order - left]
                for left in range(1, order)
            )
            output.append(sp.cancel((self.values[order] - middle) / (2 * output[0])))
        return ThetaJet(
            tuple(output) + (sp.S.Zero,) * (COEFFICIENT_JET_ORDER + 1 - len(output)),
            self.valid_through,
        )

    def derivative(self, axis: int) -> "ThetaJet":
        if axis != THETA_AXIS:
            return ZERO
        if self.valid_through == 0:
            raise ValueError("coefficient derivative exhausted authoritative jet depth")
        if self.is_zero:
            return ZERO
        return ThetaJet(self.values[1:] + (sp.S.Zero,), self.valid_through - 1)

    def jet(self, word: Sequence[int]) -> sp.Rational:
        if any(axis != THETA_AXIS for axis in word):
            return sp.S.Zero
        order = len(word)
        if order > self.valid_through:
            raise ValueError("requested coefficient derivative exceeds authoritative jet depth")
        return self.values[order]

    @property
    def base(self) -> sp.Rational:
        return self.values[0]

    @property
    def is_zero(self) -> bool:
        return all(value == 0 for value in self.values[: self.valid_through + 1])


def as_theta(value: object) -> ThetaJet:
    return value if isinstance(value, ThetaJet) else ThetaJet.constant(value)


ZERO = ThetaJet.constant(0)
ONE = ThetaJet.constant(1)
SIN = ThetaJet.sin_equator()
COS = ThetaJet.cos_equator()
COT = COS / SIN


@dataclass(frozen=True)
class LinearOperator:
    terms: tuple[tuple[int, tuple[int, ...], ThetaJet], ...] = ()

    @staticmethod
    def from_terms(terms: Iterable[tuple[int, Sequence[int], object]]) -> "LinearOperator":
        combined: dict[tuple[int, tuple[int, ...]], ThetaJet] = {}
        for component, word, coefficient in terms:
            key = (int(component), tuple(sorted(int(axis) for axis in word)))
            combined[key] = combined.get(key, ZERO) + as_theta(coefficient)
        return LinearOperator(tuple((*key, value) for key, value in sorted(combined.items()) if not value.is_zero))

    @staticmethod
    def basis(component: int) -> "LinearOperator":
        return LinearOperator(((component, (), ONE),))

    def __add__(self, other: "LinearOperator") -> "LinearOperator":
        return LinearOperator.from_terms((*self.terms, *other.terms))

    def __neg__(self) -> "LinearOperator":
        return self.scale(-1)

    def __sub__(self, other: "LinearOperator") -> "LinearOperator":
        return self + (-other)

    def scale(self, coefficient: object) -> "LinearOperator":
        coefficient = as_theta(coefficient)
        return LinearOperator.from_terms((component, word, coefficient * value) for component, word, value in self.terms)

    def derivative(self, axis: int) -> "LinearOperator":
        return LinearOperator.from_terms(
            term
            for component, word, coefficient in self.terms
            for term in (
                (component, word, coefficient.derivative(axis)),
                (component, (*word, axis), coefficient),
            )
        )

    @property
    def maximum_total_order(self) -> int:
        return max((len(word) for _, word, _ in self.terms), default=-1)


LZERO = LinearOperator()


@dataclass(frozen=True)
class BilinearOperator:
    terms: tuple[tuple[int, tuple[int, ...], int, tuple[int, ...], ThetaJet], ...] = ()

    @staticmethod
    def from_terms(terms: Iterable[tuple[int, Sequence[int], int, Sequence[int], object]]) -> "BilinearOperator":
        combined: dict[tuple[int, tuple[int, ...], int, tuple[int, ...]], ThetaJet] = {}
        for left, left_word, right, right_word, coefficient in terms:
            key = (int(left), tuple(sorted(left_word)), int(right), tuple(sorted(right_word)))
            combined[key] = combined.get(key, ZERO) + as_theta(coefficient)
        return BilinearOperator(tuple((*key, value) for key, value in sorted(combined.items()) if not value.is_zero))

    def __add__(self, other: "BilinearOperator") -> "BilinearOperator":
        return BilinearOperator.from_terms((*self.terms, *other.terms))

    def __neg__(self) -> "BilinearOperator":
        return self.scale(-1)

    def __sub__(self, other: "BilinearOperator") -> "BilinearOperator":
        return self + (-other)

    def scale(self, coefficient: object) -> "BilinearOperator":
        coefficient = as_theta(coefficient)
        return BilinearOperator.from_terms((a, aw, b, bw, coefficient * value) for a, aw, b, bw, value in self.terms)

    def derivative(self, axis: int) -> "BilinearOperator":
        return BilinearOperator.from_terms(
            term
            for a, aw, b, bw, coefficient in self.terms
            for term in (
                (a, aw, b, bw, coefficient.derivative(axis)),
                (a, (*aw, axis), b, bw, coefficient),
                (a, aw, b, (*bw, axis), coefficient),
            )
        )

    def koszul_swapped(self, parities: Sequence[int]) -> "BilinearOperator":
        return BilinearOperator.from_terms(
            (b, bw, a, aw, (-1 if parities[a] * parities[b] else 1) * coefficient)
            for a, aw, b, bw, coefficient in self.terms
        )

    @property
    def maximum_total_order(self) -> int:
        return max((len(aw) + len(bw) for _, aw, _, bw, _ in self.terms), default=-1)


BZERO = BilinearOperator()


@dataclass(frozen=True)
class TrilinearOperator:
    terms: tuple[tuple[int, tuple[int, ...], int, tuple[int, ...], int, tuple[int, ...], ThetaJet], ...] = ()

    @staticmethod
    def from_terms(terms: Iterable[tuple]) -> "TrilinearOperator":
        combined: dict[tuple, ThetaJet] = {}
        for a, aw, b, bw, c, cw, coefficient in terms:
            key = (int(a), tuple(sorted(aw)), int(b), tuple(sorted(bw)), int(c), tuple(sorted(cw)))
            combined[key] = combined.get(key, ZERO) + as_theta(coefficient)
        return TrilinearOperator(tuple((*key, value) for key, value in sorted(combined.items()) if not value.is_zero))

    def __add__(self, other: "TrilinearOperator") -> "TrilinearOperator":
        return TrilinearOperator.from_terms((*self.terms, *other.terms))

    def __neg__(self) -> "TrilinearOperator":
        return self.scale(-1)

    def __sub__(self, other: "TrilinearOperator") -> "TrilinearOperator":
        return self + (-other)

    def scale(self, coefficient: object) -> "TrilinearOperator":
        coefficient = as_theta(coefficient)
        return TrilinearOperator.from_terms((a, aw, b, bw, c, cw, coefficient * value) for a, aw, b, bw, c, cw, value in self.terms)

    def derivative(self, axis: int) -> "TrilinearOperator":
        return TrilinearOperator.from_terms(
            term
            for a, aw, b, bw, c, cw, coefficient in self.terms
            for term in (
                (a, aw, b, bw, c, cw, coefficient.derivative(axis)),
                (a, (*aw, axis), b, bw, c, cw, coefficient),
                (a, aw, b, (*bw, axis), c, cw, coefficient),
                (a, aw, b, bw, c, (*cw, axis), coefficient),
            )
        )

    def koszul_permuted(self, order: tuple[int, int, int], parities: Sequence[int]) -> "TrilinearOperator":
        terms = []
        for a, aw, b, bw, c, cw, coefficient in self.terms:
            slots = ((a, aw), (b, bw), (c, cw))
            exponent = sum(
                parities[slots[order[left]][0]] * parities[slots[order[right]][0]]
                for left in range(3) for right in range(left + 1, 3)
                if order[left] > order[right]
            )
            terms.append((
                slots[order[0]][0], slots[order[0]][1],
                slots[order[1]][0], slots[order[1]][1],
                slots[order[2]][0], slots[order[2]][1],
                (-1 if exponent % 2 else 1) * coefficient,
            ))
        return TrilinearOperator.from_terms(terms)

    @property
    def maximum_total_order(self) -> int:
        return max((len(aw) + len(bw) + len(cw) for _, aw, _, bw, _, cw, _ in self.terms), default=-1)


TZERO = TrilinearOperator()


def _sum_linear(values: Iterable[LinearOperator]) -> LinearOperator:
    return LinearOperator.from_terms(term for value in values for term in value.terms)


def _sum_bilinear(values: Iterable[BilinearOperator]) -> BilinearOperator:
    return BilinearOperator.from_terms(term for value in values for term in value.terms)


def _sum_trilinear(values: Iterable[TrilinearOperator]) -> TrilinearOperator:
    return TrilinearOperator.from_terms(term for value in values for term in value.terms)


def _outer(first: LinearOperator, second: LinearOperator) -> BilinearOperator:
    return BilinearOperator.from_terms((a, aw, b, bw, av * bv) for a, aw, av in first.terms for b, bw, bv in second.terms)


def _outer3(first: LinearOperator, second: LinearOperator, third: LinearOperator) -> TrilinearOperator:
    return TrilinearOperator.from_terms((a, aw, b, bw, c, cw, av * bv * cv) for a, aw, av in first.terms for b, bw, bv in second.terms for c, cw, cv in third.terms)


def _sym_outer3(first: LinearOperator, second: LinearOperator, third: LinearOperator) -> TrilinearOperator:
    values = (first, second, third)
    return _sum_trilinear(_outer3(values[o[0]], values[o[1]], values[o[2]]) for o in permutations(range(3)))


def _sym_linear_bilinear(linear: LinearOperator, bilinear: BilinearOperator) -> TrilinearOperator:
    return TrilinearOperator.from_terms(
        term for a, aw, av in linear.terms for b, bw, c, cw, value in bilinear.terms
        for term in (
            (a, aw, b, bw, c, cw, av * value),
            (b, bw, a, aw, c, cw, av * value),
            (b, bw, c, cw, a, aw, av * value),
        )
    )


@dataclass(frozen=True)
class TaylorJet:
    background: ThetaJet = ZERO
    linear: LinearOperator = LZERO
    bilinear: BilinearOperator = BZERO
    trilinear: TrilinearOperator = TZERO

    @staticmethod
    def constant(value: object) -> "TaylorJet":
        return TaylorJet(as_theta(value))

    @staticmethod
    def field(component: int, background: object = ZERO) -> "TaylorJet":
        return TaylorJet(as_theta(background), LinearOperator.basis(component))

    def __add__(self, other: "TaylorJet") -> "TaylorJet":
        return TaylorJet(self.background + other.background, self.linear + other.linear, self.bilinear + other.bilinear, self.trilinear + other.trilinear)

    def __neg__(self) -> "TaylorJet":
        return self.scale(-1)

    def __sub__(self, other: "TaylorJet") -> "TaylorJet":
        return self + (-other)

    def scale(self, coefficient: object) -> "TaylorJet":
        coefficient = as_theta(coefficient)
        return TaylorJet(self.background * coefficient, self.linear.scale(coefficient), self.bilinear.scale(coefficient), self.trilinear.scale(coefficient))

    def __mul__(self, other: "TaylorJet") -> "TaylorJet":
        return TaylorJet(
            self.background * other.background,
            _sum_linear(
                (
                    self.linear.scale(other.background),
                    other.linear.scale(self.background),
                )
            ),
            _sum_bilinear(
                (
                    self.bilinear.scale(other.background),
                    other.bilinear.scale(self.background),
                    _outer(self.linear, other.linear),
                    _outer(other.linear, self.linear),
                )
            ),
            _sum_trilinear(
                (
                    self.trilinear.scale(other.background),
                    other.trilinear.scale(self.background),
                    _sym_linear_bilinear(self.linear, other.bilinear),
                    _sym_linear_bilinear(other.linear, self.bilinear),
                )
            ),
        )

    def reciprocal(self) -> "TaylorJet":
        inverse = self.background.reciprocal()
        return TaylorJet(
            inverse,
            self.linear.scale(-(inverse * inverse)),
            _sum_bilinear(
                (
                    self.bilinear.scale(-(inverse * inverse)),
                    _outer(self.linear, self.linear).scale(2 * inverse.power(3)),
                )
            ),
            _sum_trilinear(
                (
                    self.trilinear.scale(-(inverse * inverse)),
                    _sym_linear_bilinear(self.linear, self.bilinear).scale(
                        2 * inverse.power(3)
                    ),
                    _outer3(self.linear, self.linear, self.linear).scale(
                        -6 * inverse.power(4)
                    ),
                )
            ),
        )

    def __truediv__(self, other: "TaylorJet") -> "TaylorJet":
        return self * other.reciprocal()

    def power(self, exponent: int) -> "TaylorJet":
        if exponent < 0:
            return self.reciprocal().power(-exponent)
        output = TaylorJet.constant(1)
        for _ in range(exponent):
            output = output * self
        return output

    def derivative(self, axis: int) -> "TaylorJet":
        return TaylorJet(self.background.derivative(axis), self.linear.derivative(axis), self.bilinear.derivative(axis), self.trilinear.derivative(axis))

    def sqrt(self) -> "TaylorJet":
        root = self.background.sqrt()
        first = root.reciprocal().scale(sp.Rational(1, 2)) if hasattr(root, "scale") else root.reciprocal() * sp.Rational(1, 2)
        second = self.background.power(-1) * first * sp.Rational(-1, 2)
        third = self.background.power(-2) * first * sp.Rational(3, 4)
        return TaylorJet(
            root,
            self.linear.scale(first),
            _sum_bilinear(
                (
                    self.bilinear.scale(first),
                    _outer(self.linear, self.linear).scale(second),
                )
            ),
            _sum_trilinear(
                (
                    self.trilinear.scale(first),
                    _sym_linear_bilinear(self.linear, self.bilinear).scale(second),
                    _outer3(self.linear, self.linear, self.linear).scale(third),
                )
            ),
        )


JZERO = TaylorJet()


def sum_jets(values: Iterable[TaylorJet]) -> TaylorJet:
    values = tuple(values)
    if not values:
        return JZERO
    return TaylorJet(
        sum((value.background for value in values), ZERO),
        _sum_linear(value.linear for value in values),
        _sum_bilinear(value.bilinear for value in values),
        _sum_trilinear(value.trilinear for value in values),
    )


def metric_jet() -> dict[tuple[int, int], TaylorJet]:
    background = {(a, b): ZERO for a, b in product(range(4), repeat=2)}
    background[(0, 0)] = ThetaJet.constant(-1)
    background[(1, 1)] = ONE
    background[(2, 2)] = ONE
    background[(3, 3)] = SIN * SIN
    return {(a, b): TaylorJet.field(PAIR_INDEX[tuple(sorted((a, b)))], background[(a, b)]) for a, b in product(range(4), repeat=2)}


def inverse_metric(metric: dict[tuple[int, int], TaylorJet]) -> dict[tuple[int, int], TaylorJet]:
    background_inverse = {(a, b): ZERO for a, b in product(range(4), repeat=2)}
    background_inverse[(0, 0)] = ThetaJet.constant(-1)
    background_inverse[(1, 1)] = ONE
    background_inverse[(2, 2)] = ONE
    background_inverse[(3, 3)] = (SIN * SIN).reciprocal()
    output = {}
    # The metric jet is symmetric at every Taylor order.  Construct each
    # inverse component once instead of independently canonicalizing the two
    # equal PBW expressions for (a,b) and (b,a).
    for a, b in PAIRS:
        linear = _sum_linear(
            metric[(i, j)].linear.scale(-background_inverse[(a, i)] * background_inverse[(j, b)])
            for i, j in product(range(4), repeat=2)
            if not (background_inverse[(a, i)] * background_inverse[(j, b)]).is_zero
        )
        bilinear = _sum_bilinear(
            (_outer(metric[(i, j)].linear, metric[(k, l)].linear) + _outer(metric[(k, l)].linear, metric[(i, j)].linear)).scale(
                coefficient
            )
            for i, j, k, l in product(range(4), repeat=4)
            if not (
                coefficient := background_inverse[(a, i)]
                * background_inverse[(j, k)]
                * background_inverse[(l, b)]
            ).is_zero
        )
        trilinear = _sum_trilinear(
            _sym_outer3(metric[(i, j)].linear, metric[(k, l)].linear, metric[(m, n)].linear).scale(
                -coefficient
            )
            for i, j, k, l, m, n in product(range(4), repeat=6)
            if not (
                coefficient := background_inverse[(a, i)]
                * background_inverse[(j, k)]
                * background_inverse[(l, m)]
                * background_inverse[(n, b)]
            ).is_zero
        )
        value = TaylorJet(background_inverse[(a, b)], linear, bilinear, trilinear)
        output[(a, b)] = value
        output[(b, a)] = value
    return output


def determinant(metric: dict[tuple[int, int], TaylorJet]) -> TaylorJet:
    values = []
    for permutation in permutations(range(4)):
        inversions = sum(permutation[a] > permutation[b] for a in range(4) for b in range(a + 1, 4))
        value = TaylorJet.constant(-1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            value = value * metric[(row, column)]
        values.append(value)
    return sum_jets(values)


def connection(metric: dict[tuple[int, int], TaylorJet], inverse: dict[tuple[int, int], TaylorJet]) -> dict[tuple[int, int, int], TaylorJet]:
    output = {}
    # Levi-Civita torsion-freeness makes the two lower connection slots
    # symmetric.  Aliasing the exact value is important here: downstream
    # Riemann and Bach construction otherwise repeats 24 large trilinear
    # canonicalizations without adding information.
    for target in range(4):
        for left, right in PAIRS:
            value = sum_jets(
                inverse[(target, index)]
                * (
                    metric[(index, right)].derivative(left)
                    + metric[(index, left)].derivative(right)
                    - metric[(left, right)].derivative(index)
                ).scale(sp.Rational(1, 2))
                for index in range(4)
            )
            output[(target, left, right)] = value
            output[(target, right, left)] = value
    return output


def covariant_derivative(tensor: dict[tuple[int, ...], TaylorJet], variance: tuple[int, ...], gamma: dict[tuple[int, int, int], TaylorJet]) -> dict[tuple[int, ...], TaylorJet]:
    output = {}
    for axis in range(4):
        for indices in product(range(4), repeat=len(variance)):
            value = tensor.get(indices, JZERO).derivative(axis)
            for position, sign in enumerate(variance):
                current = indices[position]
                if sign == -1:
                    value = value - sum_jets(
                        gamma[(replacement, axis, current)] * tensor.get(indices[:position] + (replacement,) + indices[position + 1:], JZERO)
                        for replacement in range(4)
                    )
                else:
                    value = value + sum_jets(
                        gamma[(current, axis, replacement)] * tensor.get(indices[:position] + (replacement,) + indices[position + 1:], JZERO)
                        for replacement in range(4)
                    )
            output[(axis, *indices)] = value
    return output


@lru_cache(maxsize=1)
def metric_geometry() -> dict[str, object]:
    metric = metric_jet()
    inverse = inverse_metric(metric)
    gamma = connection(metric, inverse)
    riemann = {}
    for target, vector in product(range(4), repeat=2):
        for first in range(4):
            riemann[(target, vector, first, first)] = JZERO
        for first in range(4):
            for second in range(first + 1, 4):
                value = gamma[(target, second, vector)].derivative(first)
                value = value - gamma[(target, first, vector)].derivative(second)
                value = value + sum_jets(
                    gamma[(middle, second, vector)] * gamma[(target, first, middle)]
                    - gamma[(middle, first, vector)] * gamma[(target, second, middle)]
                    for middle in range(4)
                )
                riemann[(target, vector, first, second)] = value
                riemann[(target, vector, second, first)] = -value
    ricci = {}
    for a, b in PAIRS:
        value = sum_jets(riemann[(index, a, index, b)] for index in range(4))
        ricci[(a, b)] = value
        ricci[(b, a)] = value
    scalar = sum_jets(inverse[(a, b)] * ricci[(a, b)] for a, b in product(range(4), repeat=2))
    volume_ratio = determinant(metric).scale(-1).sqrt().scale(SIN.reciprocal())
    return {"metric": metric, "inverse": inverse, "connection": gamma, "riemann": riemann, "ricci": ricci, "scalar": scalar, "volume_ratio": volume_ratio}


def operation_record(operator: LinearOperator | BilinearOperator | TrilinearOperator, *, output_row: int, coefficient_jet_order: int = 2) -> list[dict[str, object]]:
    records = []
    for term in operator.terms:
        if isinstance(operator, LinearOperator):
            component, word, coefficient = term
            inputs = [{"row": component, "word": list(word)}]
        elif isinstance(operator, BilinearOperator):
            a, aw, b, bw, coefficient = term
            inputs = [{"row": a, "word": list(aw)}, {"row": b, "word": list(bw)}]
        else:
            a, aw, b, bw, c, cw, coefficient = term
            inputs = [{"row": a, "word": list(aw)}, {"row": b, "word": list(bw)}, {"row": c, "word": list(cw)}]
        jets = []
        for order in range(coefficient_jet_order + 1):
            for word in combinations_with_replacement(range(4), order):
                value = coefficient.jet(word)
                if value != 0:
                    jets.append({"word": list(word), "coefficient": str(value)})
        if jets:
            records.append({"output_row": output_row, "inputs": inputs, "coefficient": str(coefficient.base), "coefficient_jets": jets})
    return records


def compose_linear(outer: LinearOperator, inner_rows: Sequence[LinearOperator]) -> LinearOperator:
    terms = []
    for middle, word, coefficient in outer.terms:
        current = inner_rows[middle]
        for axis in word:
            current = current.derivative(axis)
        terms.extend((component, inner_word, coefficient * value) for component, inner_word, value in current.terms)
    return LinearOperator.from_terms(terms)


def formal_adjoint_scalar(operator: LinearOperator) -> LinearOperator:
    divergence = (ZERO, ZERO, COT, ZERO)
    output = LZERO
    for component, word, coefficient in operator.terms:
        states = LinearOperator(((component, (), coefficient),))
        for axis in reversed(word):
            states = LinearOperator.from_terms(
                term
                for source, source_word, value in states.terms
                for term in (
                    (source, source_word, -value.derivative(axis) - divergence[axis] * value),
                    (source, (*source_word, axis), -value),
                )
            )
        output = output + states
    return output


def formal_adjoint_matrix(matrix: Sequence[Sequence[LinearOperator]]) -> tuple[tuple[LinearOperator, ...], ...]:
    rows = len(matrix)
    columns = len(matrix[0]) if rows else 0
    if any(len(row) != columns for row in matrix):
        raise ValueError("ragged operator matrix")
    output = [[LZERO for _ in range(rows)] for _ in range(columns)]
    for row in range(rows):
        for column in range(columns):
            adjoint = formal_adjoint_scalar(matrix[row][column])
            output[column][row] = LinearOperator.from_terms(
                (row, word, coefficient) for _source, word, coefficient in adjoint.terms
            )
    return tuple(tuple(row) for row in output)


def graded_complete_bilinear(operator: BilinearOperator, parities: Sequence[int]) -> BilinearOperator:
    return operator + operator.koszul_swapped(parities)


def graded_complete_trilinear(operator: TrilinearOperator, parities: Sequence[int]) -> TrilinearOperator:
    return _sum_trilinear(operator.koszul_permuted(order, parities) for order in permutations(range(3)))


def _adjoint_product_states(
    word: tuple[int, ...],
    other_words: tuple[tuple[int, ...], ...],
    coefficient: ThetaJet,
) -> tuple[tuple[tuple[tuple[int, ...], ...], tuple[int, ...], ThetaJet], ...]:
    divergence = (ZERO, ZERO, COT, ZERO)
    states: dict[tuple[tuple[tuple[int, ...], ...], tuple[int, ...]], ThetaJet] = {(other_words, ()): coefficient}
    for axis in reversed(word):
        updated: dict[tuple[tuple[tuple[int, ...], ...], tuple[int, ...]], ThetaJet] = {}
        for (current_others, dual_word), value in states.items():
            def add(key, amount):
                updated[key] = updated.get(key, ZERO) + amount

            add((current_others, dual_word), -value.derivative(axis) - divergence[axis] * value)
            for position in range(len(current_others)):
                changed = list(current_others)
                changed[position] = tuple(sorted((*changed[position], axis)))
                add((tuple(changed), dual_word), -value)
            add((current_others, tuple(sorted((*dual_word, axis)))), -value)
        states = updated
    return tuple((others, dual, value) for (others, dual), value in states.items() if not value.is_zero)


def negative_transpose_bilinear_right(operator: BilinearOperator, *, dual_output: int) -> dict[int, BilinearOperator]:
    grouped: dict[int, list[tuple]] = {}
    for left, left_word, right, right_word, coefficient in operator.terms:
        for (new_left,), dual_word, value in _adjoint_product_states(right_word, (left_word,), coefficient):
            grouped.setdefault(right, []).append((left, new_left, dual_output, dual_word, -value))
    return {row: BilinearOperator.from_terms(terms) for row, terms in grouped.items()}


def negative_transpose_bilinear_left(operator: BilinearOperator, *, dual_output: int) -> dict[int, BilinearOperator]:
    grouped: dict[int, list[tuple]] = {}
    for left, left_word, right, right_word, coefficient in operator.terms:
        for (new_right,), dual_word, value in _adjoint_product_states(left_word, (right_word,), coefficient):
            grouped.setdefault(left, []).append((right, new_right, dual_output, dual_word, -value))
    return {row: BilinearOperator.from_terms(terms) for row, terms in grouped.items()}


def negative_transpose_trilinear_slot(operator: TrilinearOperator, *, slot: int, dual_output: int) -> dict[int, TrilinearOperator]:
    if slot not in (0, 1, 2):
        raise ValueError("trilinear slot must be zero, one, or two")
    grouped: dict[int, list[tuple]] = {}
    for first, first_word, second, second_word, third, third_word, coefficient in operator.terms:
        rows = (first, second, third)
        words = (first_word, second_word, third_word)
        selected = rows[slot]
        other_rows = tuple(rows[index] for index in range(3) if index != slot)
        other_words = tuple(words[index] for index in range(3) if index != slot)
        for new_words, dual_word, value in _adjoint_product_states(words[slot], other_words, coefficient):
            grouped.setdefault(selected, []).append((
                other_rows[0], new_words[0], other_rows[1], new_words[1], dual_output, dual_word, -value,
            ))
    return {row: TrilinearOperator.from_terms(terms) for row, terms in grouped.items()}
