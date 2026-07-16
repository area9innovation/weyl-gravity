#!/usr/bin/env python3
"""Arbitrary-input support-local Berger ``q2`` producer.

This module starts from the covariant Weyl-plus-two-scalar action at the
rational positive Berger fixture.  It expands the exact equations in two
independent perturbations and represents the mixed coefficient as a sparse
bilinear PBW operator in the invariant frame.  The construction is deliberately
action-first: the already-certified 54-row unary complex is used as a
regression target, never as a fit for the quadratic coefficients.

The first implementation gate is the metric Bach block.  Later stages in this
same producer add the polar-clock equations, the minimal gauge/antifield
completion, and the two certified linear canonical transformations.  Until
all stages and their independent checks pass, no support-local q2 certificate
is emitted.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
from pathlib import Path
import sys
from typing import Iterable

import sympy as sp

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import (
    ETA,
    PAIRS,
    PAIR_INDEX,
    ALPHA_B,
    U,
    V,
    LinearOperator,
    _background_geometry,
    _linearized_curvature,
    _linearized_matter,
    _operator_matrix,
    _adjoint_matrix,
    build_linearized_bach_matrix,
    _canonical_equation_weights,
    _matrix_record,
    _pbw_word,
)


SQRT10 = sp.sqrt(10)
U0 = 3 * SQRT10 / 20
V0 = 2 * SQRT10 / 3
ALPHA0 = sp.Integer(5)
RHO0 = sp.Integer(1)
OMEGA0 = sp.Rational(3, 4)
LAMBDA0 = sp.Rational(119, 480)
RHO_BAR, CLOCK_OMEGA, CLOCK_LAMBDA = sp.symbols(
    "rho_bar clock_omega clock_lambda", nonzero=True, real=True
)
FIELD_RANK = 12


@lru_cache(maxsize=None)
def _simp(value: sp.Expr) -> sp.Expr:
    """Normalize the polynomial coefficient field ``Q[u,v,alpha_B]``.

    No field-dependent denominator occurs at this perturbative order, so a full
    rational-function ``cancel/factor`` at every sparse addition is needless
    and very expensive.  ``expand`` gives a canonical polynomial normal form
    and keeps the exact calculation small.
    """

    return sp.expand(value)


def _structure(first: int, second: int) -> dict[int, sp.Expr]:
    table = {
        (1, 2): {3: U},
        (2, 1): {3: -U},
        (2, 3): {1: V},
        (3, 2): {1: -V},
        (3, 1): {2: V},
        (1, 3): {2: -V},
    }
    return table.get((first, second), {})


@dataclass(frozen=True)
class BilinearOperator:
    """Scalar bilinear differential operator on two twelve-field inputs."""

    terms: tuple[
        tuple[int, tuple[int, ...], int, tuple[int, ...], sp.Expr], ...
    ] = ()

    @staticmethod
    def from_terms(
        terms: Iterable[
            tuple[int, tuple[int, ...], int, tuple[int, ...], sp.Expr]
        ],
    ) -> "BilinearOperator":
        combined: dict[
            tuple[int, tuple[int, ...], int, tuple[int, ...]], sp.Expr
        ] = {}
        for left, left_word, right, right_word, coefficient in terms:
            if coefficient == 0:
                continue
            for reduced_left, left_coefficient in _pbw_word(tuple(left_word)):
                for reduced_right, right_coefficient in _pbw_word(tuple(right_word)):
                    key = (left, reduced_left, right, reduced_right)
                    combined[key] = (
                        combined.get(key, sp.S.Zero)
                        + coefficient * left_coefficient * right_coefficient
                    )
        normalized = []
        for key, coefficient in sorted(combined.items()):
            value = _simp(coefficient)
            if value != 0:
                normalized.append((*key, value))
        return BilinearOperator(tuple(normalized))

    def __add__(self, other: "BilinearOperator") -> "BilinearOperator":
        return BilinearOperator.from_terms((*self.terms, *other.terms))

    def __neg__(self) -> "BilinearOperator":
        return BilinearOperator.from_terms(
            (left, left_word, right, right_word, -coefficient)
            for left, left_word, right, right_word, coefficient in self.terms
        )

    def __sub__(self, other: "BilinearOperator") -> "BilinearOperator":
        return self + (-other)

    def scale(self, coefficient: sp.Expr) -> "BilinearOperator":
        return BilinearOperator.from_terms(
            (left, left_word, right, right_word, coefficient * value)
            for left, left_word, right, right_word, value in self.terms
        )

    def derivative(self, axis: int) -> "BilinearOperator":
        # The invariant derivative acts on the product, hence on both inputs.
        return BilinearOperator.from_terms(
            term
            for left, left_word, right, right_word, coefficient in self.terms
            for term in (
                (left, (axis, *left_word), right, right_word, coefficient),
                (left, left_word, right, (axis, *right_word), coefficient),
            )
        )

    def swapped(self) -> "BilinearOperator":
        return BilinearOperator.from_terms(
            (right, right_word, left, left_word, coefficient)
            for left, left_word, right, right_word, coefficient in self.terms
        )

    def koszul_swapped(self, parities: tuple[int, ...]) -> "BilinearOperator":
        """Exchange the inputs with the declared unsuspended Koszul sign."""

        return BilinearOperator.from_terms(
            (
                right,
                right_word,
                left,
                left_word,
                (-1 if parities[left] * parities[right] else 1) * coefficient,
            )
            for left, left_word, right, right_word, coefficient in self.terms
        )

    @property
    def maximum_total_order(self) -> int:
        return max(
            (len(left_word) + len(right_word) for _, left_word, _, right_word, _ in self.terms),
            default=-1,
        )


BZERO = BilinearOperator()


def _sum_linear(values: Iterable[LinearOperator]) -> LinearOperator:
    output = LinearOperator()
    for value in values:
        output = output + value
    return output


def _sum_bilinear(values: Iterable[BilinearOperator]) -> BilinearOperator:
    output = BZERO
    for value in values:
        output = output + value
    return output


FIXTURE_SUBSTITUTION = {
    U: U0,
    V: V0,
    ALPHA_B: ALPHA0,
    RHO_BAR: RHO0,
    CLOCK_OMEGA: OMEGA0,
    CLOCK_LAMBDA: LAMBDA0,
}


def _fixture_linear(operator: LinearOperator) -> LinearOperator:
    return LinearOperator.from_terms(
        (component, word, coefficient.subs(FIXTURE_SUBSTITUTION))
        for component, word, coefficient in operator.terms
    )


def _fixture_bilinear(operator: BilinearOperator) -> BilinearOperator:
    return BilinearOperator.from_terms(
        (
            left,
            left_word,
            right,
            right_word,
            coefficient.subs(FIXTURE_SUBSTITUTION),
        )
        for left, left_word, right, right_word, coefficient in operator.terms
    )


def _outer(left: LinearOperator, right: LinearOperator) -> BilinearOperator:
    return BilinearOperator.from_terms(
        (left_component, left_word, right_component, right_word, left_value * right_value)
        for left_component, left_word, left_value in left.terms
        for right_component, right_word, right_value in right.terms
    )


def _shift_inputs(operator: BilinearOperator, offset: int) -> BilinearOperator:
    return BilinearOperator.from_terms(
        (left + offset, left_word, right + offset, right_word, coefficient)
        for left, left_word, right, right_word, coefficient in operator.terms
    )


def _leibniz_adjoint_terms(
    word: tuple[int, ...],
    left_word: tuple[int, ...],
    right_word: tuple[int, ...],
) -> tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...]:
    """Expand the formal adjoint derivative on a product.

    The returned multiplicity is integral.  PBW normalization is applied by
    ``BilinearOperator.from_terms`` after all derivative distributions are
    generated.
    """

    states: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {
        (left_word, right_word): 1
    }
    # (D_word)^sharp=(-1)^len(word) D_reverse(word).  Acting on the product
    # proceeds inner-to-outer, hence in the original word order.
    for axis in word:
        updated: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {}
        for (left, right), multiplicity in states.items():
            for key in (((axis, *left), right), (left, (axis, *right))):
                updated[key] = updated.get(key, 0) + multiplicity
        states = updated
    sign = -1 if len(word) % 2 else 1
    return tuple((left, right, sign * multiplicity) for (left, right), multiplicity in states.items())


def _leibniz_output_terms(
    word: tuple[int, ...],
    left_word: tuple[int, ...],
    right_word: tuple[int, ...],
) -> tuple[tuple[tuple[int, ...], tuple[int, ...], int], ...]:
    """Expand an output derivative on a bilinear product."""

    states: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {
        (left_word, right_word): 1
    }
    # D_word acts inner-to-outer in reverse tuple order.
    for axis in reversed(word):
        updated: dict[tuple[tuple[int, ...], tuple[int, ...]], int] = {}
        for (left, right), multiplicity in states.items():
            for key in (((axis, *left), right), (left, (axis, *right))):
                updated[key] = updated.get(key, 0) + multiplicity
        states = updated
    return tuple((left, right, multiplicity) for (left, right), multiplicity in states.items())


def _negative_transpose_right(
    operator: BilinearOperator,
    *,
    dual_output: int,
) -> dict[int, BilinearOperator]:
    """Return ``-B(c,.)^sharp`` grouped by its field-antifield output."""

    grouped: dict[int, list[tuple[int, tuple[int, ...], int, tuple[int, ...], sp.Expr]]] = {}
    for left, left_word, right, right_word, coefficient in operator.terms:
        for new_left_word, dual_word, multiplicity in _leibniz_adjoint_terms(
            right_word, left_word, ()
        ):
            grouped.setdefault(right, []).append(
                (
                    left,
                    new_left_word,
                    dual_output,
                    dual_word,
                    -coefficient * multiplicity,
                )
            )
    return {output: BilinearOperator.from_terms(terms) for output, terms in grouped.items()}


def _negative_transpose_left(
    operator: BilinearOperator,
    *,
    dual_output: int,
) -> dict[int, BilinearOperator]:
    """Return ``-B(.,x)^sharp`` grouped by its ghost-antifield output."""

    grouped: dict[int, list[tuple[int, tuple[int, ...], int, tuple[int, ...], sp.Expr]]] = {}
    for left, left_word, right, right_word, coefficient in operator.terms:
        for new_right_word, dual_word, multiplicity in _leibniz_adjoint_terms(
            left_word, right_word, ()
        ):
            grouped.setdefault(left, []).append(
                (
                    right,
                    new_right_word,
                    dual_output,
                    dual_word,
                    -coefficient * multiplicity,
                )
            )
    return {output: BilinearOperator.from_terms(terms) for output, terms in grouped.items()}


RAW_PARITIES = (1,) * 5 + (0,) * 12 + (1,) * 12 + (0,) * 5
GAUGE_FIXED_PARITIES = (
    (1,) * 5
    + (0,) * 12
    + (0,) * 5
    + (0,) * 5
    + (1,) * 12
    + (1,) * 5
    + (1,) * 5
    + (0,) * 5
)
FRAME_TO_GHOST = {0: 3, 1: 0, 2: 1, 3: 2}


def _graded_complete_ordered(operator: BilinearOperator) -> BilinearOperator:
    """Add the Koszul-swapped input order to an ordered local operation."""

    swapped_terms = []
    for left, left_word, right, right_word, coefficient in operator.terms:
        sign = -1 if RAW_PARITIES[left] * RAW_PARITIES[right] else 1
        swapped_terms.append((right, right_word, left, left_word, sign * coefficient))
    return operator + BilinearOperator.from_terms(swapped_terms)


@dataclass(frozen=True)
class Jet2:
    """Background, first variation, and mixed second variation of a scalar."""

    background: sp.Expr = sp.S.Zero
    linear: LinearOperator = LinearOperator()
    bilinear: BilinearOperator = BZERO

    @staticmethod
    def constant(value: sp.Expr) -> "Jet2":
        return Jet2(_simp(value))

    @staticmethod
    def field(component: int, background: sp.Expr = sp.S.Zero) -> "Jet2":
        return Jet2(_simp(background), LinearOperator.basis(component), BZERO)

    def __add__(self, other: "Jet2") -> "Jet2":
        return Jet2(
            _simp(self.background + other.background),
            self.linear + other.linear,
            self.bilinear + other.bilinear,
        )

    def __neg__(self) -> "Jet2":
        return self.scale(-1)

    def __sub__(self, other: "Jet2") -> "Jet2":
        return self + (-other)

    def scale(self, coefficient: sp.Expr) -> "Jet2":
        return Jet2(
            _simp(coefficient * self.background),
            self.linear.scale(coefficient),
            self.bilinear.scale(coefficient),
        )

    def __mul__(self, other: "Jet2") -> "Jet2":
        return Jet2(
            _simp(self.background * other.background),
            self.linear.scale(other.background) + other.linear.scale(self.background),
            self.bilinear.scale(other.background)
            + other.bilinear.scale(self.background)
            + _outer(self.linear, other.linear)
            + _outer(other.linear, self.linear),
        )

    def reciprocal(self) -> "Jet2":
        if self.background == 0:
            raise ZeroDivisionError("Jet2 reciprocal needs a nonzero background")
        inverse = _simp(1 / self.background)
        return Jet2(
            inverse,
            self.linear.scale(-inverse**2),
            self.bilinear.scale(-inverse**2)
            + _outer(self.linear, self.linear).scale(2 * inverse**3),
        )

    def __truediv__(self, other: "Jet2") -> "Jet2":
        return self * other.reciprocal()

    def derivative(self, axis: int) -> "Jet2":
        return Jet2(sp.S.Zero, self.linear.derivative(axis), self.bilinear.derivative(axis))

    def power(self, exponent: int) -> "Jet2":
        if exponent < 0:
            return self.reciprocal().power(-exponent)
        output = Jet2.constant(1)
        for _ in range(exponent):
            output = output * self
        return output


JZERO = Jet2()


def _sum_jets(values: Iterable[Jet2]) -> Jet2:
    output = JZERO
    for value in values:
        output = output + value
    return output


def _metric() -> dict[tuple[int, int], Jet2]:
    return {
        (first, second): Jet2.field(
            PAIR_INDEX[tuple(sorted((first, second)))], ETA[first, second]
        )
        for first, second in product(range(4), repeat=2)
    }


def _inverse_metric(metric: dict[tuple[int, int], Jet2]) -> dict[tuple[int, int], Jet2]:
    # Matrix inverse through mixed perturbative order, evaluated by the
    # convergent formal identity G^{-1}=eta^{-1}-eta^{-1}h eta^{-1}
    # +eta^{-1}h eta^{-1}h eta^{-1}+O(h^3).
    output: dict[tuple[int, int], Jet2] = {}
    for first, second in product(range(4), repeat=2):
        linear = _sum_linear(
            metric[(left, right)].linear.scale(-ETA[first, left] * ETA[right, second])
            for left, right in product(range(4), repeat=2)
        )
        bilinear = _sum_bilinear(
            (
                _outer(metric[(left, middle)].linear, metric[(right, other)].linear)
                + _outer(metric[(right, other)].linear, metric[(left, middle)].linear)
            ).scale(ETA[first, left] * ETA[middle, right] * ETA[other, second])
            for left, middle, right, other in product(range(4), repeat=4)
        )
        output[(first, second)] = Jet2(ETA[first, second], linear, bilinear)
    return output


def _connection(
    metric: dict[tuple[int, int], Jet2],
    inverse: dict[tuple[int, int], Jet2],
) -> dict[tuple[int, int, int], Jet2]:
    lowered: dict[tuple[int, int, int], Jet2] = {}
    for derivative, vector, target in product(range(4), repeat=3):
        value = (
            metric[(vector, target)].derivative(derivative)
            + metric[(derivative, target)].derivative(vector)
            - metric[(derivative, vector)].derivative(target)
        )
        value = value + _sum_jets(
            metric[(target, middle)].scale(coefficient)
            for middle, coefficient in _structure(derivative, vector).items()
        )
        value = value - _sum_jets(
            metric[(derivative, middle)].scale(coefficient)
            for middle, coefficient in _structure(vector, target).items()
        )
        value = value - _sum_jets(
            metric[(vector, middle)].scale(coefficient)
            for middle, coefficient in _structure(derivative, target).items()
        )
        lowered[(target, derivative, vector)] = value.scale(sp.Rational(1, 2))
    return {
        (target, derivative, vector): _sum_jets(
            inverse[(target, lowered_target)] * lowered[(lowered_target, derivative, vector)]
            for lowered_target in range(4)
        )
        for target, derivative, vector in product(range(4), repeat=3)
    }


def _covariant_derivative(
    tensor: dict[tuple[int, ...], Jet2],
    variance: tuple[int, ...],
    connection: dict[tuple[int, int, int], Jet2],
) -> dict[tuple[int, ...], Jet2]:
    output: dict[tuple[int, ...], Jet2] = {}
    for axis in range(4):
        for indices in product(range(4), repeat=len(variance)):
            value = tensor.get(indices, JZERO).derivative(axis)
            for position, sign in enumerate(variance):
                current = indices[position]
                if sign == -1:
                    value = value - _sum_jets(
                        connection[(replacement, axis, current)]
                        * tensor.get(
                            indices[:position] + (replacement,) + indices[position + 1 :],
                            JZERO,
                        )
                        for replacement in range(4)
                    )
                else:
                    value = value + _sum_jets(
                        connection[(current, axis, replacement)]
                        * tensor.get(
                            indices[:position] + (replacement,) + indices[position + 1 :],
                            JZERO,
                        )
                        for replacement in range(4)
                    )
            output[(axis, *indices)] = value
    return output


@lru_cache(maxsize=1)
def build_metric_geometry() -> dict[str, object]:
    metric = _metric()
    inverse = _inverse_metric(metric)
    connection = _connection(metric, inverse)
    riemann: dict[tuple[int, int, int, int], Jet2] = {}
    for target, vector, first, second in product(range(4), repeat=4):
        riemann[(target, vector, first, second)] = (
            connection[(target, second, vector)].derivative(first)
            - connection[(target, first, vector)].derivative(second)
            + _sum_jets(
                connection[(middle, second, vector)] * connection[(target, first, middle)]
                - connection[(middle, first, vector)] * connection[(target, second, middle)]
                for middle in range(4)
            )
            - _sum_jets(
                connection[(target, middle, vector)].scale(coefficient)
                for middle, coefficient in _structure(first, second).items()
            )
        )
    ricci = {
        (first, second): _sum_jets(
            riemann[(index, first, index, second)] for index in range(4)
        )
        for first, second in product(range(4), repeat=2)
    }
    scalar = _sum_jets(
        inverse[(first, second)] * ricci[(first, second)]
        for first, second in product(range(4), repeat=2)
    )
    schouten = {
        (first, second): (
            ricci[(first, second)] - metric[(first, second)] * scalar.scale(sp.Rational(1, 6))
        ).scale(sp.Rational(1, 2))
        for first, second in product(range(4), repeat=2)
    }
    weyl: dict[tuple[int, int, int, int], Jet2] = {}
    for a, b, c, d in product(range(4), repeat=4):
        lowered_riemann = _sum_jets(
            metric[(a, target)] * riemann[(target, b, c, d)]
            for target in range(4)
        )
        weyl[(a, b, c, d)] = lowered_riemann - (
            metric[(a, c)] * schouten[(d, b)]
            - metric[(a, d)] * schouten[(c, b)]
            - metric[(b, c)] * schouten[(d, a)]
            + metric[(b, d)] * schouten[(c, a)]
        )
    return {
        "metric": metric,
        "inverse": inverse,
        "connection": connection,
        "riemann": riemann,
        "ricci": ricci,
        "scalar": scalar,
        "schouten": schouten,
        "weyl": weyl,
    }


@lru_cache(maxsize=1)
def build_bach_tensor() -> dict[tuple[int, int], Jet2]:
    geometry = build_metric_geometry()
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    connection = geometry["connection"]
    schouten = geometry["schouten"]
    weyl = geometry["weyl"]
    derivative_p = _covariant_derivative(schouten, (-1, -1), connection)
    second_p = _covariant_derivative(derivative_p, (-1, -1, -1), connection)
    p_up = {
        (first, second): _sum_jets(
            inverse[(first, left)] * inverse[(second, right)] * schouten[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        for first, second in product(range(4), repeat=2)
    }
    output: dict[tuple[int, int], Jet2] = {}
    for first, second in product(range(4), repeat=2):
        laplacian = _sum_jets(
            inverse[(outer, inner)] * second_p[(outer, inner, first, second)]
            for outer, inner in product(range(4), repeat=2)
        )
        mixed = _sum_jets(
            inverse[(outer, inner)] * second_p[(outer, first, second, inner)]
            for outer, inner in product(range(4), repeat=2)
        )
        curvature = _sum_jets(
            p_up[(inner, outer)] * weyl[(first, inner, second, outer)]
            for inner, outer in product(range(4), repeat=2)
        )
        output[(first, second)] = laplacian - mixed + curvature
    return output


@lru_cache(maxsize=1)
def build_clock_equations() -> dict[str, object]:
    """Return the exact polar-clock stress tensor and scalar Euler rows."""

    geometry = build_metric_geometry()
    metric = geometry["metric"]
    inverse = geometry["inverse"]
    connection = geometry["connection"]
    ricci = geometry["ricci"]
    scalar = geometry["scalar"]

    rho = Jet2.field(10, RHO_BAR)
    theta_variation = Jet2.field(11)
    d_rho = {axis: rho.derivative(axis) for axis in range(4)}
    d_theta = {
        axis: theta_variation.derivative(axis)
        + Jet2.constant(CLOCK_OMEGA if axis == 0 else 0)
        for axis in range(4)
    }
    rho_squared = rho * rho
    kinetic = _sum_jets(
        inverse[(first, second)]
        * (
            d_rho[first] * d_rho[second]
            + rho_squared * d_theta[first] * d_theta[second]
        )
        for first, second in product(range(4), repeat=2)
    )
    einstein = {
        (first, second): ricci[(first, second)]
        - metric[(first, second)] * scalar.scale(sp.Rational(1, 2))
        for first, second in product(range(4), repeat=2)
    }

    rho2_gradient = _covariant_derivative({(): rho_squared}, (), connection)
    rho2_hessian = _covariant_derivative(rho2_gradient, (-1,), connection)
    rho2_box = _sum_jets(
        inverse[(first, second)] * rho2_hessian[(first, second)]
        for first, second in product(range(4), repeat=2)
    )
    stress: dict[tuple[int, int], Jet2] = {}
    for first, second in product(range(4), repeat=2):
        minimal = (
            d_rho[first] * d_rho[second]
            + rho_squared * d_theta[first] * d_theta[second]
            - metric[(first, second)] * kinetic.scale(sp.Rational(1, 2))
            - metric[(first, second)]
            * rho.power(4).scale(CLOCK_LAMBDA / 4)
        )
        improvement = (
            einstein[(first, second)] * rho_squared
            + metric[(first, second)] * rho2_box
            - rho2_hessian[(first, second)]
        ).scale(sp.Rational(1, 6))
        stress[(first, second)] = minimal + improvement

    rho_gradient = _covariant_derivative({(): rho}, (), connection)
    rho_hessian = _covariant_derivative(rho_gradient, (-1,), connection)
    rho_box = _sum_jets(
        inverse[(first, second)] * rho_hessian[(first, second)]
        for first, second in product(range(4), repeat=2)
    )
    theta_squared = _sum_jets(
        inverse[(first, second)] * d_theta[first] * d_theta[second]
        for first, second in product(range(4), repeat=2)
    )
    rho_equation = (
        rho_box
        - rho * theta_squared
        - scalar * rho.scale(sp.Rational(1, 6))
        - rho.power(3).scale(CLOCK_LAMBDA)
    )

    current = {
        (first,): _sum_jets(
            rho_squared * inverse[(first, second)] * d_theta[second]
            for second in range(4)
        )
        for first in range(4)
    }
    derivative_current = _covariant_derivative(current, (1,), connection)
    theta_equation = _sum_jets(
        derivative_current[(axis, axis)] for axis in range(4)
    )
    return {
        "rho": rho,
        "d_theta": d_theta,
        "stress": stress,
        "rho_equation": rho_equation,
        "theta_equation": theta_equation,
    }


@lru_cache(maxsize=1)
def _volume_density_ratio() -> Jet2:
    """Return ``sqrt(-g)/sqrt(-g_bar)`` through mixed second order.

    Canonical BV antifields pair with Euler *densities*.  The distinction
    from the undensitized tensor equations is invisible in the Hessian on an
    on-shell background, but is essential at arity two.
    """

    metric = _metric()
    trace = _sum_linear(
        metric[(first, second)].linear.scale(ETA[first, second])
        for first, second in product(range(4), repeat=2)
    )
    contraction = _sum_bilinear(
        _outer(
            metric[(first, second)].linear,
            metric[(third, fourth)].linear,
        ).scale(ETA[first, third] * ETA[second, fourth])
        for first, second, third, fourth in product(range(4), repeat=4)
    )
    return Jet2(
        sp.S.One,
        trace.scale(sp.Rational(1, 2)),
        _outer(trace, trace).scale(sp.Rational(1, 4))
        - contraction.scale(sp.Rational(1, 2)),
    )


@lru_cache(maxsize=1)
def build_raw_euler_rows() -> tuple[Jet2, ...]:
    """Coupled raw Euler rows in canonical symmetric-component order."""

    bach = build_bach_tensor()
    clock = build_clock_equations()
    inverse = build_metric_geometry()["inverse"]
    density = _volume_density_ratio()
    lower_equation = {
        pair: bach[pair].scale(ALPHA_B) - clock["stress"][pair]
        for pair in product(range(4), repeat=2)
    }
    metric_rows = []
    for first, second in PAIRS:
        # The canonical coordinate is g_ab, whereas Bach and stress are
        # naturally emitted with lower indices.  The variational BV row is
        # therefore -sqrt(-g) E^{ab}, with an extra factor two for an
        # off-diagonal symmetric component.  Using only the background
        # raising matrix gives the right Hessian but the wrong q2.
        multiplicity = 2 if first != second else 1
        raised = _sum_jets(
            inverse[(first, left)]
            * inverse[(second, right)]
            * lower_equation[(left, right)]
            for left, right in product(range(4), repeat=2)
        )
        metric_rows.append(raised.scale(-multiplicity) * density)
    # The metric BV row is normalized as ``alpha_B B_ab-T_ab``, i.e. twice
    # the variational derivative with respect to the covariant metric
    # component.  The scalar Euler rows therefore carry the same factor two
    # in the canonical field--antifield pairing.  This is forced (rather than
    # chosen) by the exact dressed-clock Hessian split below.
    return (
        *metric_rows,
        clock["rho_equation"].scale(2) * density,
        clock["theta_equation"].scale(2) * density,
    )


def _raw_gauge_field_action() -> tuple[BilinearOperator, ...]:
    """Nonlinear Diff x Weyl action on ``(h,rho,theta)`` fluctuations."""

    outputs: list[BilinearOperator] = [BZERO for _ in range(FIELD_RANK)]
    # Raw global row order is ghosts_5, fields_12, antifields_12, ghost*_5.
    for first, second in PAIRS:
        output = PAIR_INDEX[(first, second)]
        terms = []
        metric_component = 5 + output
        for vector in range(4):
            ghost = FRAME_TO_GHOST[vector]
            # xi^c e_c h_ab
            terms.append((ghost, (), metric_component, (vector,), sp.S.One))
            # h_db e_a xi^d and h_ad e_b xi^d
            first_metric = 5 + PAIR_INDEX[tuple(sorted((vector, second)))]
            second_metric = 5 + PAIR_INDEX[tuple(sorted((first, vector)))]
            terms.append((ghost, (first,), first_metric, (), sp.S.One))
            terms.append((ghost, (second,), second_metric, (), sp.S.One))
            # Frame-commutator corrections in L_xi h.
            for target, coefficient in _structure(vector, first).items():
                target_metric = 5 + PAIR_INDEX[tuple(sorted((target, second)))]
                terms.append((ghost, (), target_metric, (), -coefficient))
            for target, coefficient in _structure(vector, second).items():
                target_metric = 5 + PAIR_INDEX[tuple(sorted((first, target)))]
                terms.append((ghost, (), target_metric, (), -coefficient))
        terms.append((4, (), metric_component, (), sp.Integer(2)))
        ordered = BilinearOperator.from_terms(terms)
        outputs[output] = ordered + ordered.swapped()

    rho_terms = []
    theta_terms = []
    for vector in range(4):
        ghost = FRAME_TO_GHOST[vector]
        rho_terms.append((ghost, (), 15, (vector,), sp.S.One))
        theta_terms.append((ghost, (), 16, (vector,), sp.S.One))
    rho_terms.append((4, (), 15, (), -sp.S.One))
    rho_action = BilinearOperator.from_terms(rho_terms)
    theta_action = BilinearOperator.from_terms(theta_terms)
    outputs[10] = rho_action + rho_action.swapped()
    outputs[11] = theta_action + theta_action.swapped()
    return tuple(outputs)


def _raw_ghost_bracket() -> tuple[BilinearOperator, ...]:
    """The local Lie-algebra bracket of Diff semidirect Weyl ghosts."""

    outputs: list[BilinearOperator] = [BZERO for _ in range(5)]
    for target in range(4):
        output = FRAME_TO_GHOST[target]
        terms = []
        for vector in range(4):
            ghost = FRAME_TO_GHOST[vector]
            terms.append((ghost, (), output, (vector,), sp.S.One))
            terms.append((output, (vector,), ghost, (), -sp.S.One))
        for left, right in product(range(4), repeat=2):
            coefficient = _structure(left, right).get(target, sp.S.Zero)
            if coefficient:
                terms.append(
                    (FRAME_TO_GHOST[left], (), FRAME_TO_GHOST[right], (), coefficient)
                )
        outputs[output] = BilinearOperator.from_terms(terms)
    sigma_terms = []
    for vector in range(4):
        ghost = FRAME_TO_GHOST[vector]
        sigma_terms.append((ghost, (), 4, (vector,), sp.S.One))
        sigma_terms.append((4, (vector,), ghost, (), -sp.S.One))
    outputs[4] = BilinearOperator.from_terms(sigma_terms)
    return tuple(outputs)


@lru_cache(maxsize=1)
def build_raw_minimal_q2() -> tuple[BilinearOperator, ...]:
    """Complete raw 34-row minimal q2 before clock dressing/gauge fixing."""

    outputs: list[BilinearOperator] = [BZERO for _ in range(34)]
    ghost_bracket = _raw_ghost_bracket()
    for output, operator in enumerate(ghost_bracket):
        outputs[output] = outputs[output] + operator

    gauge_action = _raw_gauge_field_action()
    for local_output, operator in enumerate(gauge_action):
        global_output = 5 + local_output
        outputs[global_output] = outputs[global_output] + operator
        ordered_gauge_field = BilinearOperator.from_terms(
            term
            for term in operator.terms
            if term[0] < 5 and 5 <= term[2] < 17
        )
        # The two cyclic mates are generated from the same local vertex.
        for field_input, mate in _negative_transpose_right(
            ordered_gauge_field, dual_output=17 + local_output
        ).items():
            outputs[17 + (field_input - 5)] = (
                outputs[17 + (field_input - 5)] + _graded_complete_ordered(mate)
            )
        for ghost_input, mate in _negative_transpose_left(
            ordered_gauge_field, dual_output=17 + local_output
        ).items():
            outputs[29 + ghost_input] = (
                outputs[29 + ghost_input] + _graded_complete_ordered(mate)
            )

    for local_output, equation in enumerate(build_raw_euler_rows()):
        outputs[17 + local_output] = outputs[17 + local_output] + _shift_inputs(
            equation.bilinear, 5
        )

    # Coadjoint ghost rows from the same bracket vertex.
    for local_output, operator in enumerate(ghost_bracket):
        for ghost_input, mate in _negative_transpose_right(
            operator, dual_output=29 + local_output
        ).items():
            outputs[29 + ghost_input] = (
                outputs[29 + ghost_input] + _graded_complete_ordered(mate)
            )
    return tuple(outputs)


def _zero_linear_matrix(rows: int, columns: int) -> list[list[LinearOperator]]:
    return [[LinearOperator() for _ in range(columns)] for _ in range(rows)]


def _one_linear(value: sp.Expr = sp.S.One) -> LinearOperator:
    return LinearOperator.from_terms(((0, (), value),))


def _multiply_linear(
    outer: list[list[LinearOperator]] | tuple[tuple[LinearOperator, ...], ...],
    inner: list[list[LinearOperator]] | tuple[tuple[LinearOperator, ...], ...],
) -> list[list[LinearOperator]]:
    if len(outer[0]) != len(inner):
        raise ValueError("linear matrix shape mismatch")
    output = _zero_linear_matrix(len(outer), len(inner[0]))
    supports = {
        middle: [(column, value) for column, value in enumerate(inner[middle]) if value.terms]
        for middle in range(len(inner))
    }
    for row, entries in enumerate(outer):
        for middle, left in enumerate(entries):
            if not left.terms:
                continue
            for column, right in supports[middle]:
                output[row][column] = output[row][column] + left.compose(right)
    return output


def _apply_output_linear(
    outer: LinearOperator, inner: BilinearOperator
) -> BilinearOperator:
    terms = []
    for outer_component, outer_word, outer_coefficient in outer.terms:
        if outer_component != 0:
            raise ValueError("matrix entry must be a scalar one-input operator")
        for left, left_word, right, right_word, coefficient in inner.terms:
            for new_left, new_right, multiplicity in _leibniz_output_terms(
                outer_word, left_word, right_word
            ):
                terms.append(
                    (
                        left,
                        new_left,
                        right,
                        new_right,
                        outer_coefficient * coefficient * multiplicity,
                    )
                )
    return BilinearOperator.from_terms(terms)


def _precompose_bilinear(
    operator: BilinearOperator,
    input_map: list[list[LinearOperator]],
) -> BilinearOperator:
    """Substitute ``old=input_map*new`` in both bilinear inputs."""

    terms = []
    supports = {
        old: [(new, entry) for new, entry in enumerate(row) if entry.terms]
        for old, row in enumerate(input_map)
    }
    for left, left_word, right, right_word, coefficient in operator.terms:
        for new_left, left_entry in supports[left]:
            for left_component, left_inner_word, left_value in left_entry.terms:
                if left_component != 0:
                    raise ValueError("input map entry must be scalar")
                for new_right, right_entry in supports[right]:
                    for right_component, right_inner_word, right_value in right_entry.terms:
                        if right_component != 0:
                            raise ValueError("input map entry must be scalar")
                        terms.append(
                            (
                                new_left,
                                left_word + left_inner_word,
                                new_right,
                                right_word + right_inner_word,
                                coefficient * left_value * right_value,
                            )
                        )
    return BilinearOperator.from_terms(terms)


def _precompose_bilinear_slot(
    operator: BilinearOperator,
    input_map: list[list[LinearOperator]] | tuple[tuple[LinearOperator, ...], ...],
    *,
    slot: int,
    parities: tuple[int, ...],
    second_slot_q1_sign: bool = False,
) -> BilinearOperator:
    """Insert a unary differential operator in one input of a bilinear row.

    ``second_slot_q1_sign`` implements the sign ``(-1)^|x|`` in the
    arity-two L-infinity identity.  It is deliberately attached after the
    substitution, hence to the external left-input component.
    """

    if slot not in (0, 1):
        raise ValueError("bilinear input slot must be zero or one")
    supports = {
        old: [(new, entry) for new, entry in enumerate(row) if entry.terms]
        for old, row in enumerate(input_map)
    }
    terms = []
    for left, left_word, right, right_word, coefficient in operator.terms:
        if slot == 0:
            for new_left, entry in supports[left]:
                for component, inner_word, value in entry.terms:
                    if component != 0:
                        raise ValueError("unary matrix entry must be scalar")
                    terms.append(
                        (
                            new_left,
                            left_word + inner_word,
                            right,
                            right_word,
                            coefficient * value,
                        )
                    )
        else:
            for new_right, entry in supports[right]:
                for component, inner_word, value in entry.terms:
                    if component != 0:
                        raise ValueError("unary matrix entry must be scalar")
                    sign = -1 if second_slot_q1_sign and parities[left] else 1
                    terms.append(
                        (
                            left,
                            left_word,
                            new_right,
                            right_word + inner_word,
                            sign * coefficient * value,
                        )
                    )
    return BilinearOperator.from_terms(terms)


def arity_two_nilpotency_defect(
    q1: list[list[LinearOperator]] | tuple[tuple[LinearOperator, ...], ...],
    q2: tuple[BilinearOperator, ...] | list[BilinearOperator],
    parities: tuple[int, ...],
    *,
    fixture_normal_form: bool = False,
) -> tuple[BilinearOperator, ...]:
    """Return ``q1 q2+q2(q1,.)+(-1)^|.|q2(.,q1)`` coefficientwise."""

    if len(q1) != len(q2) or len(parities) != len(q2):
        raise ValueError("q1/q2/parity dimensions disagree")
    output: list[BilinearOperator] = []
    for target, q2_row in enumerate(q2):
        defect = BZERO
        for middle, outer in enumerate(q1[target]):
            if outer.terms and q2[middle].terms:
                defect = defect + _apply_output_linear(outer, q2[middle])
        if q2_row.terms:
            defect = defect + _precompose_bilinear_slot(
                q2_row, q1, slot=0, parities=parities
            )
            defect = defect + _precompose_bilinear_slot(
                q2_row,
                q1,
                slot=1,
                parities=parities,
                second_slot_q1_sign=True,
            )
        # Composition concatenates PBW words and can therefore introduce the
        # symbolic frame commutator coefficients U,V even when both operands
        # were already evaluated at the rational fixture.  Specialization is
        # consequently a final-normal-form operation, not only an input
        # operation.
        output.append(_fixture_bilinear(defect) if fixture_normal_form else defect)
    return tuple(output)


def raw_physical_cyclicity_defect(
    q2: tuple[BilinearOperator, ...] | list[BilinearOperator],
    *,
    fixture_normal_form: bool = False,
) -> tuple[BilinearOperator, ...]:
    """Check the Helmholtz/cyclicity transpose of the physical cubic vertex.

    The physical part of row ``17+i`` is the second variation of the
    canonical Euler density.  Transposing its first field input through the
    invariant volume form must reproduce the corresponding row ``17+j``.
    This is the coefficientwise local-functional version of total symmetry of
    the third action derivative.
    """

    predicted: list[list[tuple[int, tuple[int, ...], int, tuple[int, ...], sp.Expr]]] = [
        [] for _ in range(FIELD_RANK)
    ]
    actual: list[BilinearOperator] = []
    for equation in range(FIELD_RANK):
        physical = BilinearOperator.from_terms(
            term
            for term in q2[17 + equation].terms
            if 5 <= term[0] < 17 and 5 <= term[2] < 17
        )
        actual.append(physical)
        for left, left_word, right, right_word, coefficient in physical.terms:
            transposed_equation = left - 5
            for differentiated_right, differentiated_output, multiplicity in _leibniz_adjoint_terms(
                left_word, right_word, ()
            ):
                predicted[transposed_equation].append(
                    (
                        5 + equation,
                        differentiated_output,
                        right,
                        differentiated_right,
                        coefficient * multiplicity,
                    )
                )
    defects = []
    for equation in range(FIELD_RANK):
        produced = BilinearOperator.from_terms(predicted[equation])
        defect = produced - actual[equation]
        defects.append(_fixture_bilinear(defect) if fixture_normal_form else defect)
    return tuple(defects)


def _transform_bilinear_vector(
    operators: tuple[BilinearOperator, ...] | list[BilinearOperator],
    output_map: list[list[LinearOperator]],
    input_map: list[list[LinearOperator]],
) -> tuple[BilinearOperator, ...]:
    """Apply one linear canonical change of variables to a q2 vector."""

    precomposed = [
        _precompose_bilinear(operator, input_map) if operator.terms else BZERO
        for operator in operators
    ]
    output = []
    for new_output, row in enumerate(output_map):
        value = BZERO
        for old_output, outer in enumerate(row):
            if outer.terms and precomposed[old_output].terms:
                value = value + _apply_output_linear(outer, precomposed[old_output])
        output.append(value)
    return tuple(output)


def _clock_canonical_maps_fixture() -> tuple[list[list[LinearOperator]], list[list[LinearOperator]]]:
    """Return raw-to-dressed canonical map and its inverse on 34 rows."""

    from d_quotient_classical.backreacted_clock.berger_full_gauge_companion import (
        full_metric_gauge,
    )

    metric_gauge = full_metric_gauge()
    # The helper is written in covector components, whereas the clock row is
    # tau=xi^0.  Raising the Lorentzian time component contributes one minus.
    tau_column = [
        _fixture_linear(metric_gauge[row][3]).scale(-1) for row in range(10)
    ]
    field_inverse = _zero_linear_matrix(12, 12)  # dressed -> raw
    field_map = _zero_linear_matrix(12, 12)      # raw -> dressed
    for index in range(10):
        field_inverse[index][index] = _one_linear()
        field_inverse[index][10] = _one_linear(-2 * ETA[PAIRS[index]])
        field_inverse[index][11] = tau_column[index]
        field_map[index][index] = _one_linear()
        field_map[index][10] = _one_linear(2 * ETA[PAIRS[index]] / RHO0)
        field_map[index][11] = tau_column[index].scale(-1 / OMEGA0)
    field_inverse[10][10] = _one_linear(RHO0)
    field_inverse[11][11] = _one_linear(OMEGA0)
    field_map[10][10] = _one_linear(1 / RHO0)
    field_map[11][11] = _one_linear(1 / OMEGA0)

    canonical = _zero_linear_matrix(34, 34)
    inverse = _zero_linear_matrix(34, 34)
    for index in (*range(5), *range(29, 34)):
        canonical[index][index] = _one_linear()
        inverse[index][index] = _one_linear()
    field_inverse_adjoint = _adjoint_matrix(field_inverse)
    field_map_adjoint = _adjoint_matrix(field_map)
    for row in range(12):
        for column in range(12):
            canonical[5 + row][5 + column] = field_map[row][column]
            inverse[5 + row][5 + column] = field_inverse[row][column]
            canonical[17 + row][17 + column] = field_inverse_adjoint[row][column]
            inverse[17 + row][17 + column] = field_map_adjoint[row][column]
    return canonical, inverse


@lru_cache(maxsize=1)
def build_dressed_minimal_q1_fixture() -> tuple[tuple[LinearOperator, ...], ...]:
    canonical, inverse = _clock_canonical_maps_fixture()
    transformed = _multiply_linear(
        _multiply_linear(canonical, build_raw_minimal_q1_fixture()), inverse
    )
    # PBW composition reintroduces the symbolic frame commutator coefficients;
    # specialize once more after the final product.
    return tuple(tuple(_fixture_linear(entry) for entry in row) for row in transformed)


@lru_cache(maxsize=1)
def build_dressed_minimal_q2_fixture() -> tuple[BilinearOperator, ...]:
    """Transport the complete raw minimal q2 through the clock dressing."""

    canonical, inverse = _clock_canonical_maps_fixture()
    raw = tuple(_fixture_bilinear(operator) for operator in build_raw_minimal_q2())
    transformed = _transform_bilinear_vector(raw, canonical, inverse)
    return tuple(_fixture_bilinear(operator) for operator in transformed)


def _reindex_bilinear(
    operator: BilinearOperator, index_map: dict[int, int]
) -> BilinearOperator:
    return BilinearOperator.from_terms(
        (
            index_map[left],
            left_word,
            index_map[right],
            right_word,
            coefficient,
        )
        for left, left_word, right, right_word, coefficient in operator.terms
    )


@lru_cache(maxsize=1)
def build_gauge_fixed_54_q2_fixture() -> tuple[BilinearOperator, ...]:
    """Apply the certified nonminimal extension and gauge-fermion shear."""

    from d_quotient_classical.backreacted_clock.berger_gauge_fixed_nonminimal_completion import (
        _gauge_fermion_shear,
    )
    from d_quotient_classical.backreacted_clock.berger_nonminimal_algebraic_completion import (
        MINIMAL_TO_EXTENDED,
    )

    minimal = build_dressed_minimal_q2_fixture()
    index_map = {old: new for old, new in enumerate(MINIMAL_TO_EXTENDED)}
    extended = [BZERO for _ in range(54)]
    for old_output, new_output in enumerate(MINIMAL_TO_EXTENDED):
        extended[new_output] = _reindex_bilinear(minimal[old_output], index_map)
    _raw_map, _condition, _nilpotent, shear, inverse = _gauge_fermion_shear()
    transformed = _transform_bilinear_vector(extended, shear, inverse)
    return tuple(_fixture_bilinear(operator) for operator in transformed)


@lru_cache(maxsize=1)
def build_raw_minimal_q1_fixture() -> tuple[tuple[LinearOperator, ...], ...]:
    """Raw 34-row tangent differential at the rational positive fixture."""

    from d_quotient_classical.backreacted_clock.berger_full_gauge_companion import (
        full_metric_gauge,
    )

    gauge = _zero_linear_matrix(12, 5)
    metric_gauge = full_metric_gauge()
    for row in range(10):
        for column in range(5):
            sign = -1 if column == 3 else 1
            gauge[row][column] = _fixture_linear(metric_gauge[row][column]).scale(sign)
    gauge[10][4] = _one_linear(-RHO0)
    gauge[11][3] = _one_linear(OMEGA0)

    # Reconstruct the Hessian without asking the q2 engine for its mixed
    # coefficient.  This keeps unary regression fast and independent.
    clock = build_clock_equations()
    bach = build_linearized_bach_matrix()
    weights = _canonical_equation_weights()
    linear_euler: list[LinearOperator] = []
    for row, pair in enumerate(PAIRS):
        bach_row = LinearOperator.from_terms(
            (column, word, coefficient)
            for column in range(10)
            for _, word, coefficient in bach[row][column].terms
        ).scale(ALPHA_B)
        stress_row = clock["stress"][pair].linear.scale(weights[row, row])
        linear_euler.append(bach_row - stress_row)
    linear_euler.extend(
        (
            clock["rho_equation"].linear.scale(2),
            clock["theta_equation"].linear.scale(2),
        )
    )

    hessian = _zero_linear_matrix(12, 12)
    for row, equation in enumerate(linear_euler):
        fixture = _fixture_linear(equation)
        for column in range(12):
            hessian[row][column] = LinearOperator.from_terms(
                (0, word, coefficient)
                for component, word, coefficient in fixture.terms
                if component == column
            )
    minus_adjoint = _adjoint_matrix(gauge, sign=-1)
    output = _zero_linear_matrix(34, 34)
    for row in range(12):
        for column in range(5):
            output[5 + row][column] = gauge[row][column]
    for row in range(12):
        for column in range(12):
            output[17 + row][5 + column] = hessian[row][column]
    for row in range(5):
        for column in range(12):
            output[29 + row][17 + column] = minus_adjoint[row][column]
    return tuple(tuple(row) for row in output)


def metric_bach_q2() -> list[list[list[BilinearOperator]]]:
    """Return canonical metric-equation rows of ``alpha_B B^(2)``."""

    bach = build_bach_tensor()
    weights = _canonical_equation_weights()
    output = [
        [[BZERO for _ in range(FIELD_RANK)] for _ in range(FIELD_RANK)]
        for _ in range(10)
    ]
    for row, pair in enumerate(PAIRS):
        operator = bach[pair].bilinear.scale(ALPHA_B * weights[row, row])
        for left, left_word, right, right_word, coefficient in operator.terms:
            output[row][left][right] = output[row][left][right] + BilinearOperator.from_terms(
                ((left, left_word, right, right_word, coefficient),)
            )
    return output


def verify_background_and_symmetry() -> dict[str, object]:
    geometry = build_metric_geometry()
    connection = geometry["connection"]
    # Validate the exact Koszul convention against the frozen connection.
    from d_quotient_classical.backreacted_clock.berger_linearized_bach_pbw import GAMMA

    for target, derivative, vector in product(range(4), repeat=3):
        if _simp(
            connection[(target, derivative, vector)].background
            - GAMMA[target][derivative][vector]
        ) != 0:
            raise AssertionError("nonlinear connection does not reproduce the frozen Berger background")
    bach = build_bach_tensor()
    frozen = build_linearized_bach_matrix()
    weights = _canonical_equation_weights()
    for row, pair in enumerate(PAIRS):
        produced = bach[pair].linear.scale(weights[row, row])
        for column in range(10):
            produced_column = LinearOperator.from_terms(
                (0, word, coefficient)
                for component, word, coefficient in produced.terms
                if component == column
            )
            frozen_column = LinearOperator.from_terms(
                (0, word, coefficient)
                for _, word, coefficient in frozen[row][column].terms
            )
            if produced_column != frozen_column:
                raise AssertionError(
                    f"nonlinear Bach engine does not reproduce frozen q1 at {(row, column)}"
                )
    asymmetry = {
        pair: bach[pair].bilinear - bach[pair].bilinear.swapped()
        for pair in PAIRS
    }
    if any(operator.terms for operator in asymmetry.values()):
        raise AssertionError("second Bach variation is not symmetric in its inputs")
    clock = build_clock_equations()
    branch = {
        U: U0,
        V: V0,
        ALPHA_B: ALPHA0,
        RHO_BAR: RHO0,
        CLOCK_OMEGA: OMEGA0,
        CLOCK_LAMBDA: LAMBDA0,
    }
    for equation in (clock["rho_equation"], clock["theta_equation"]):
        if _simp(equation.background.subs(branch)) != 0:
            raise AssertionError("rational Berger clock background is not on shell")
        if equation.bilinear != equation.bilinear.swapped():
            raise AssertionError("clock q2 row is not symmetric in its field inputs")
    for pair in PAIRS:
        if clock["stress"][pair].bilinear != clock["stress"][pair].bilinear.swapped():
            raise AssertionError("clock stress q2 is not symmetric in its field inputs")
    frozen_matter = _operator_matrix(
        _linearized_matter(_background_geometry(), _linearized_curvature(_background_geometry()))
    )
    for row, pair in enumerate(PAIRS):
        produced = clock["stress"][pair].linear.scale(weights[row, row])
        for column in range(10):
            produced_column = LinearOperator.from_terms(
                (0, word, coefficient.subs(branch))
                for component, word, coefficient in produced.terms
                if component == column
            )
            frozen_column = LinearOperator.from_terms(
                (0, word, coefficient.subs({U: U0, V: V0, ALPHA_B: ALPHA0}))
                for _, word, coefficient in frozen_matter[row][column].terms
            )
            if produced_column != frozen_column:
                raise AssertionError(
                    f"clock stress does not reproduce frozen q1 at {(row, column)}"
                )
    from d_quotient_classical.backreacted_clock.berger_minimal_34_portable_contraction import (
        _exact_matrices as _frozen_minimal_matrices,
    )

    produced_q1 = build_dressed_minimal_q1_fixture()
    frozen_q1 = _frozen_minimal_matrices()["q_full"]
    for row, column in product(range(34), repeat=2):
        expected = _fixture_linear(frozen_q1[row][column])
        if produced_q1[row][column] != expected:
            raise AssertionError(
                f"raw action plus clock canonical map does not reproduce q1 at {(row, column)}"
            )
    return {
        "background_connection_matches_frozen_q1": True,
        "linear_Bach_matches_frozen_q1_coefficientwise": True,
        "metric_bach_q2_koszul_symmetric": True,
        "clock_background_equations_zero_at_rational_fixture": True,
        "clock_and_stress_q2_koszul_symmetric": True,
        "linear_clock_stress_matches_frozen_q1_coefficientwise": True,
        "raw_action_clock_transform_matches_all_34_frozen_q1_rows": True,
        "maximum_total_jet_order": max(
            bach[pair].bilinear.maximum_total_order for pair in PAIRS
        ),
        "metric_bach_term_count": sum(len(bach[pair].bilinear.terms) for pair in PAIRS),
        "coupled_euler_q2_term_count": sum(
            len(row.bilinear.terms) for row in build_raw_euler_rows()
        ),
    }


def main() -> int:
    checks = verify_background_and_symmetry()
    print("BERGER SUPPORT-LOCAL Q2 PHYSICAL BACH ENGINE: PASS")
    for key, value in checks.items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
