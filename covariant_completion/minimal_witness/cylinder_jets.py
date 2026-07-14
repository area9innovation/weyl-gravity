"""Exact finite-jet algebra at one point of the conformal cylinder.

The product is homogeneous under ``R x SO(4)``.  Consequently an identity
between natural differential operators of order at most four is global once
it holds on every four-jet at one point.  This module implements that local
test in stereographic spatial coordinates with

``g=-dt^2+(1+|x|^2/4)^(-2) dx^i dx^i``.

Unlike a finite harmonic cutoff, the jet basis is exhaustive for the stated
differential order.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product

import sympy as sp


DIMENSION = 4
# The ghost identity is fourth order.  The field/ghost intertwiner ``HK=KR``
# is fifth order, so the common jet algebra retains one additional order.
JET_ORDER = 5
ZERO_MULTIINDEX = (0, 0, 0, 0)


class Jet:
    """Truncated four-variable Taylor polynomial with exact coefficients."""

    __slots__ = ("coefficients",)

    def __init__(self, coefficients: dict[tuple[int, ...], object] | None = None):
        self.coefficients = {
            key: sp.sympify(value)
            for key, value in (coefficients or {}).items()
            if value != 0
        }

    @staticmethod
    def constant(value: object) -> "Jet":
        return Jet({ZERO_MULTIINDEX: value})

    @staticmethod
    def monomial(exponents: tuple[int, ...], value: object = 1) -> "Jet":
        return Jet({tuple(exponents): value})

    def __add__(self, other: object) -> "Jet":
        right = other if isinstance(other, Jet) else Jet.constant(other)
        coefficients = dict(self.coefficients)
        for key, value in right.coefficients.items():
            coefficients[key] = sp.expand(coefficients.get(key, 0) + value)
        return Jet(coefficients)

    __radd__ = __add__

    def __neg__(self) -> "Jet":
        return Jet({key: -value for key, value in self.coefficients.items()})

    def __sub__(self, other: object) -> "Jet":
        return self + (-other)

    def __rsub__(self, other: object) -> "Jet":
        return other + (-self)

    def __mul__(self, other: object) -> "Jet":
        right = other if isinstance(other, Jet) else Jet.constant(other)
        coefficients: dict[tuple[int, ...], sp.Expr] = {}
        for left_key, left_value in self.coefficients.items():
            for right_key, right_value in right.coefficients.items():
                key = tuple(
                    left_key[index] + right_key[index]
                    for index in range(DIMENSION)
                )
                if sum(key) <= JET_ORDER:
                    coefficients[key] = sp.expand(
                        coefficients.get(key, 0) + left_value * right_value
                    )
        return Jet(coefficients)

    __rmul__ = __mul__

    def derivative(self, axis: int) -> "Jet":
        coefficients: dict[tuple[int, ...], sp.Expr] = {}
        for key, value in self.coefficients.items():
            if key[axis] == 0:
                continue
            output = list(key)
            factor = output[axis]
            output[axis] -= 1
            coefficients[tuple(output)] = value * factor
        return Jet(coefficients)

    @property
    def value(self) -> sp.Expr:
        return sp.expand(self.coefficients.get(ZERO_MULTIINDEX, 0))


def _zero() -> Jet:
    return Jet.constant(0)


def _sum(values) -> Jet:
    return sum(values, _zero())


@dataclass(frozen=True)
class CylinderJetGeometry:
    """Metric jets and covariant operators at the cylinder base point."""

    metric: tuple[tuple[Jet, ...], ...]
    inverse_metric: tuple[tuple[Jet, ...], ...]
    christoffel: tuple[tuple[tuple[Jet, ...], ...], ...]
    ricci: tuple[tuple[Jet, ...], ...]
    ricci_mixed: tuple[tuple[Jet, ...], ...]
    ricci_up: tuple[tuple[Jet, ...], ...]

    @staticmethod
    def build() -> "CylinderJetGeometry":
        coordinates = tuple(
            Jet.monomial(tuple(1 if axis == index else 0 for axis in range(4)))
            for index in range(4)
        )
        radius_squared = _sum(
            coordinates[index] * coordinates[index] for index in range(1, 4)
        )
        u = Fraction(1, 4) * radius_squared
        spatial_metric = Jet.constant(1) - 2 * u + 3 * u * u
        spatial_inverse = Jet.constant(1) + 2 * u + u * u

        metric = [[_zero() for _ in range(4)] for _ in range(4)]
        inverse = [[_zero() for _ in range(4)] for _ in range(4)]
        metric[0][0] = Jet.constant(-1)
        inverse[0][0] = Jet.constant(-1)
        for index in range(1, 4):
            metric[index][index] = spatial_metric
            inverse[index][index] = spatial_inverse

        christoffel = [
            [[_zero() for _ in range(4)] for _ in range(4)]
            for _ in range(4)
        ]
        for upper in range(4):
            for left in range(4):
                for right in range(4):
                    christoffel[upper][left][right] = Fraction(1, 2) * _sum(
                        inverse[upper][contracted]
                        * (
                            metric[contracted][right].derivative(left)
                            + metric[contracted][left].derivative(right)
                            - metric[left][right].derivative(contracted)
                        )
                        for contracted in range(4)
                    )

        ricci = [[_zero() for _ in range(4)] for _ in range(4)]
        for index in range(1, 4):
            ricci[index][index] = 2 * spatial_metric
        ricci_mixed = [
            [
                _sum(
                    ricci[mu][contracted] * inverse[contracted][nu]
                    for contracted in range(4)
                )
                for nu in range(4)
            ]
            for mu in range(4)
        ]
        ricci_up = [
            [
                _sum(
                    inverse[mu][left]
                    * ricci[left][right]
                    * inverse[right][nu]
                    for left in range(4)
                    for right in range(4)
                )
                for nu in range(4)
            ]
            for mu in range(4)
        ]

        return CylinderJetGeometry(
            metric=tuple(tuple(row) for row in metric),
            inverse_metric=tuple(tuple(row) for row in inverse),
            christoffel=tuple(
                tuple(tuple(row) for row in plane) for plane in christoffel
            ),
            ricci=tuple(tuple(row) for row in ricci),
            ricci_mixed=tuple(tuple(row) for row in ricci_mixed),
            ricci_up=tuple(tuple(row) for row in ricci_up),
        )

    @staticmethod
    def zero_covector() -> list[Jet]:
        return [_zero() for _ in range(4)]

    def covariant_derivative_covector(self, covector: list[Jet]):
        return [
            [
                covector[nu].derivative(mu)
                - _sum(
                    self.christoffel[contracted][mu][nu]
                    * covector[contracted]
                    for contracted in range(4)
                )
                for nu in range(4)
            ]
            for mu in range(4)
        ]

    def covariant_derivative_symmetric(self, tensor):
        return [
            [
                [
                    tensor[mu][nu].derivative(axis)
                    - _sum(
                        self.christoffel[contracted][axis][mu]
                        * tensor[contracted][nu]
                        + self.christoffel[contracted][axis][nu]
                        * tensor[mu][contracted]
                        for contracted in range(4)
                    )
                    for nu in range(4)
                ]
                for mu in range(4)
            ]
            for axis in range(4)
        ]

    def divergence_covector(self, covector: list[Jet]) -> Jet:
        derivative = self.covariant_derivative_covector(covector)
        return _sum(
            self.inverse_metric[left][right] * derivative[left][right]
            for left in range(4)
            for right in range(4)
        )

    def divergence_symmetric(self, tensor) -> list[Jet]:
        derivative = self.covariant_derivative_symmetric(tensor)
        return [
            _sum(
                self.inverse_metric[left][right]
                * derivative[left][mu][right]
                for left in range(4)
                for right in range(4)
            )
            for mu in range(4)
        ]

    def rough_wave_covector(self, covector: list[Jet]) -> list[Jet]:
        first = self.covariant_derivative_covector(covector)
        output: list[Jet] = []
        for mu in range(4):
            value = _zero()
            for left in range(4):
                for right in range(4):
                    second = first[right][mu].derivative(left) - _sum(
                        self.christoffel[contracted][left][right]
                        * first[contracted][mu]
                        + self.christoffel[contracted][left][mu]
                        * first[right][contracted]
                        for contracted in range(4)
                    )
                    value += self.inverse_metric[left][right] * second
            output.append(value)
        return output

    def second_covariant_derivative_symmetric(self, tensor):
        first = self.covariant_derivative_symmetric(tensor)
        return [
            [
                [
                    [
                        first[first_axis][mu][nu].derivative(second_axis)
                        - _sum(
                            self.christoffel[contracted][second_axis][first_axis]
                            * first[contracted][mu][nu]
                            + self.christoffel[contracted][second_axis][mu]
                            * first[first_axis][contracted][nu]
                            + self.christoffel[contracted][second_axis][nu]
                            * first[first_axis][mu][contracted]
                            for contracted in range(4)
                        )
                        for nu in range(4)
                    ]
                    for mu in range(4)
                ]
                for first_axis in range(4)
            ]
            for second_axis in range(4)
        ]

    def rough_wave_symmetric(self, tensor):
        second = self.second_covariant_derivative_symmetric(tensor)
        return [
            [
                _sum(
                    self.inverse_metric[second_axis][first_axis]
                    * second[second_axis][first_axis][mu][nu]
                    for second_axis in range(4)
                    for first_axis in range(4)
                )
                for nu in range(4)
            ]
            for mu in range(4)
        ]

    def ricci_second_symmetric(self, tensor):
        second = self.second_covariant_derivative_symmetric(tensor)
        return [
            [
                _sum(
                    self.ricci_up[second_axis][first_axis]
                    * second[second_axis][first_axis][mu][nu]
                    for second_axis in range(4)
                    for first_axis in range(4)
                )
                for nu in range(4)
            ]
            for mu in range(4)
        ]

    def tracefree_projection(self, tensor):
        trace = _sum(
            self.inverse_metric[mu][nu] * tensor[mu][nu]
            for mu in range(4)
            for nu in range(4)
        )
        return [
            [
                tensor[mu][nu] - Fraction(1, 4) * self.metric[mu][nu] * trace
                for nu in range(4)
            ]
            for mu in range(4)
        ]

    def ricci_symmetrized_action(self, tensor, *, squared: bool = False):
        endomorphism = self.ricci_mixed
        if squared:
            endomorphism = tuple(
                tuple(
                    _sum(
                        self.ricci_mixed[mu][middle]
                        * self.ricci_mixed[middle][nu]
                        for middle in range(4)
                    )
                    for nu in range(4)
                )
                for mu in range(4)
            )
        output = [
            [
                Fraction(1, 2)
                * _sum(
                    (
                        endomorphism[mu][contracted] * tensor[contracted][nu]
                        + endomorphism[nu][contracted] * tensor[mu][contracted]
                    )
                    for contracted in range(4)
                )
                for nu in range(4)
            ]
            for mu in range(4)
        ]
        return self.tracefree_projection(output)

    def ricci_both_indices(self, tensor):
        output = [
            [
                _sum(
                    self.ricci_mixed[mu][left]
                    * self.ricci_mixed[nu][right]
                    * tensor[left][right]
                    for left in range(4)
                    for right in range(4)
                )
                for nu in range(4)
            ]
            for mu in range(4)
        ]
        return self.tracefree_projection(output)

    def ricci_rank_one(self, tensor):
        contraction = _sum(
            self.ricci_up[left][right] * tensor[left][right]
            for left in range(4)
            for right in range(4)
        )
        output = [
            [self.ricci[mu][nu] * contraction for nu in range(4)]
            for mu in range(4)
        ]
        return self.tracefree_projection(output)

    @staticmethod
    def gradient(scalar: Jet) -> list[Jet]:
        return [scalar.derivative(mu) for mu in range(4)]

    def conformal_killing(self, covector: list[Jet]):
        derivative = self.covariant_derivative_covector(covector)
        divergence = self.divergence_covector(covector)
        return [
            [
                derivative[mu][nu]
                + derivative[nu][mu]
                - Fraction(1, 2) * self.metric[mu][nu] * divergence
                for nu in range(4)
            ]
            for mu in range(4)
        ]

    def companion_terms(self, tensor):
        """Return ``T_0`` and the four independent parallel-Ricci terms."""

        divergence = self.divergence_symmetric(tensor)
        double_divergence = self.divergence_covector(divergence)
        principal = [
            wave - Fraction(1, 3) * gradient
            for wave, gradient in zip(
                self.rough_wave_covector(divergence),
                self.gradient(double_divergence),
            )
        ]
        scalar_curvature_divergence = [6 * value for value in divergence]
        ricci_divergence = [
            _sum(
                self.ricci_mixed[mu][nu] * divergence[nu]
                for nu in range(4)
            )
            for mu in range(4)
        ]
        ricci_trace = _sum(
            self.ricci_up[left][right] * tensor[left][right]
            for left in range(4)
            for right in range(4)
        )
        ricci_trace_gradient = self.gradient(ricci_trace)
        derivative = self.covariant_derivative_symmetric(tensor)
        ricci_cross_derivative = [
            _sum(
                self.ricci_up[left][right]
                * derivative[left][right][mu]
                for left in range(4)
                for right in range(4)
            )
            for mu in range(4)
        ]
        return (
            principal,
            scalar_curvature_divergence,
            ricci_divergence,
            ricci_trace_gradient,
            ricci_cross_derivative,
        )

    def completed_companion(self, tensor) -> list[Jet]:
        terms = self.companion_terms(tensor)
        coefficients = (
            sp.Integer(1),
            sp.Rational(1, 3),
            sp.Integer(-1),
            sp.Rational(1, 3),
            sp.Integer(0),
        )
        return [
            _sum(coefficients[index] * terms[index][mu] for index in range(5))
            for mu in range(4)
        ]

    def ghost_biwave(self, covector: list[Jet]) -> list[Jet]:
        wave = self.rough_wave_covector(covector)
        wave_squared = self.rough_wave_covector(wave)
        return [wave_squared[mu] + 2 * wave[mu] for mu in range(4)]

    @staticmethod
    def exhaustive_multiindices(
        maximum_order: int = JET_ORDER,
    ) -> tuple[tuple[int, ...], ...]:
        return tuple(
            key
            for key in product(range(JET_ORDER + 1), repeat=4)
            if sum(key) <= maximum_order
        )
