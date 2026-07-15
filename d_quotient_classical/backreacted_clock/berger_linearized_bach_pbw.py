#!/usr/bin/env python3
"""Exact invariant-frame PBW expansion of the Berger linearized Bach tensor.

The Berger frame has constant connection and curvature coefficients but its
spatial derivatives do not commute.  This module represents linear
differential operators in the universal enveloping algebra of the invariant
frame and reduces every word to the ordered PBW basis

``e0^n0 e1^n1 e2^n2 e3^n3``.

The Bach variation is derived from

``B_ab = Box P_ab - nabla^c nabla_a P_bc + P^{cd} C_acbd``

including variation of both inverse metrics, both covariant derivatives, the
Schouten tensor, and the background Weyl tensor.  No conformally-flat or
round-cylinder specialization is used.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import Iterable

import sympy as sp

try:
    from d_quotient_classical.backreacted_clock.berger_retained_minimal_operator import (
        PAIRS,
        _canonical_equation_weights,
        _principal_geometry,
    )
    from d_quotient_classical.backreacted_clock.berger_retained_minimal_layout import (
        BergerRetainedMinimalLayout,
    )
except ModuleNotFoundError:  # Direct script execution.
    from berger_retained_minimal_operator import (
        PAIRS,
        _canonical_equation_weights,
        _principal_geometry,
    )
    from berger_retained_minimal_layout import BergerRetainedMinimalLayout


U, V, ALPHA_B = sp.symbols("u v alpha_B", nonzero=True, real=True)
ETA = sp.diag(-1, 1, 1, 1)
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE_PATH = ROOT / "d_quotient_classical/certificates/BERGER_RETAINED_MINIMAL_OPERATOR.json"
REPORT_PATH = ROOT / "d_quotient_classical/reports/berger-retained-minimal-operator.md"
SCHEMA_PATH = ROOT / "d_quotient_classical/schema/berger-retained-minimal-operator-v1.schema.json"


def _simp(value: sp.Expr) -> sp.Expr:
    return sp.factor(sp.cancel(value))


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


@lru_cache(maxsize=None)
def _pbw_word(word: tuple[int, ...]) -> tuple[tuple[tuple[int, ...], sp.Expr], ...]:
    """Reduce a frame-derivative word to nondecreasing PBW order."""

    inversion = next(
        (index for index in range(len(word) - 1) if word[index] > word[index + 1]),
        None,
    )
    if inversion is None:
        return ((word, sp.S.One),)
    left, right = word[inversion], word[inversion + 1]
    swapped = word[:inversion] + (right, left) + word[inversion + 2 :]
    output: dict[tuple[int, ...], sp.Expr] = dict(_pbw_word(swapped))
    for target, coefficient in _structure(left, right).items():
        shorter = word[:inversion] + (target,) + word[inversion + 2 :]
        for reduced, nested in _pbw_word(shorter):
            output[reduced] = output.get(reduced, sp.S.Zero) + coefficient * nested
    return tuple(
        (reduced, _simp(coefficient))
        for reduced, coefficient in sorted(output.items())
        if _simp(coefficient) != 0
    )


@dataclass(frozen=True)
class LinearOperator:
    """Scalar linear differential operator from ten symmetric inputs."""

    terms: tuple[tuple[int, tuple[int, ...], sp.Expr], ...] = ()

    @staticmethod
    def from_terms(
        terms: Iterable[tuple[int, tuple[int, ...], sp.Expr]],
    ) -> "LinearOperator":
        combined: dict[tuple[int, tuple[int, ...]], sp.Expr] = {}
        for component, word, coefficient in terms:
            if coefficient == 0:
                continue
            for reduced, pbw_coefficient in _pbw_word(tuple(word)):
                key = (component, reduced)
                combined[key] = combined.get(key, sp.S.Zero) + coefficient * pbw_coefficient
        normalized = []
        for (component, word), coefficient in sorted(combined.items()):
            value = _simp(coefficient)
            if value != 0:
                normalized.append((component, word, value))
        return LinearOperator(tuple(normalized))

    @staticmethod
    def basis(component: int) -> "LinearOperator":
        return LinearOperator(((component, (), sp.S.One),))

    def __add__(self, other: "LinearOperator") -> "LinearOperator":
        return LinearOperator.from_terms((*self.terms, *other.terms))

    def __neg__(self) -> "LinearOperator":
        return LinearOperator.from_terms(
            (component, word, -coefficient)
            for component, word, coefficient in self.terms
        )

    def __sub__(self, other: "LinearOperator") -> "LinearOperator":
        return self + (-other)

    def scale(self, coefficient: sp.Expr) -> "LinearOperator":
        return LinearOperator.from_terms(
            (component, word, coefficient * value)
            for component, word, value in self.terms
        )

    def derivative(self, axis: int) -> "LinearOperator":
        return LinearOperator.from_terms(
            (component, (axis, *word), coefficient)
            for component, word, coefficient in self.terms
        )

    def compose(self, inner: "LinearOperator") -> "LinearOperator":
        if any(component != 0 for component, _, _ in self.terms):
            raise ValueError("compose expects a scalar one-input outer operator")
        return LinearOperator.from_terms(
            (inner_component, outer_word + inner_word, outer_coefficient * inner_coefficient)
            for _, outer_word, outer_coefficient in self.terms
            for inner_component, inner_word, inner_coefficient in inner.terms
        )

    def by_order(self, order: int) -> "LinearOperator":
        return LinearOperator.from_terms(
            (component, word, coefficient)
            for component, word, coefficient in self.terms
            if len(word) == order
        )

    @property
    def maximum_order(self) -> int:
        return max((len(word) for _, word, _ in self.terms), default=-1)


ZERO = LinearOperator()


def _sum_ops(values: Iterable[LinearOperator]) -> LinearOperator:
    result = ZERO
    for value in values:
        result = result + value
    return result


def _connection() -> list[list[list[sp.Expr]]]:
    structure = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for first, second, target, value in (
        (1, 2, 3, U),
        (2, 3, 1, V),
        (3, 1, 2, V),
    ):
        structure[first][second][target] = value
        structure[second][first][target] = -value
    gamma = [[[sp.S.Zero for _ in range(4)] for _ in range(4)] for _ in range(4)]
    for derivative, vector, lowered_target in product(range(4), repeat=3):
        lower = sp.Rational(1, 2) * (
            sum(ETA[lowered_target, middle] * structure[derivative][vector][middle] for middle in range(4))
            - sum(ETA[derivative, middle] * structure[vector][lowered_target][middle] for middle in range(4))
            + sum(ETA[vector, middle] * structure[lowered_target][derivative][middle] for middle in range(4))
        )
        for target in range(4):
            gamma[target][derivative][vector] += ETA[target, lowered_target] * lower
    return gamma


GAMMA = _connection()


def _covariant_derivative_operator(
    tensor: dict[tuple[int, ...], LinearOperator],
    variance: tuple[int, ...],
) -> dict[tuple[int, ...], LinearOperator]:
    output: dict[tuple[int, ...], LinearOperator] = {}
    for axis in range(4):
        for indices in product(range(4), repeat=len(variance)):
            value = tensor.get(indices, ZERO).derivative(axis)
            for position, sign in enumerate(variance):
                current = indices[position]
                if sign == -1:
                    correction = _sum_ops(
                        tensor.get(indices[:position] + (replacement,) + indices[position + 1 :], ZERO).scale(
                            GAMMA[replacement][axis][current]
                        )
                        for replacement in range(4)
                    )
                    value = value - correction
                else:
                    correction = _sum_ops(
                        tensor.get(indices[:position] + (replacement,) + indices[position + 1 :], ZERO).scale(
                            GAMMA[current][axis][replacement]
                        )
                        for replacement in range(4)
                    )
                    value = value + correction
            output[(axis, *indices)] = value
    return output


def _covariant_derivative_background(
    tensor: dict[tuple[int, ...], sp.Expr],
    variance: tuple[int, ...],
) -> dict[tuple[int, ...], sp.Expr]:
    output: dict[tuple[int, ...], sp.Expr] = {}
    for axis in range(4):
        for indices in product(range(4), repeat=len(variance)):
            value = sp.S.Zero
            for position, sign in enumerate(variance):
                current = indices[position]
                if sign == -1:
                    value -= sum(
                        GAMMA[replacement][axis][current]
                        * tensor.get(indices[:position] + (replacement,) + indices[position + 1 :], sp.S.Zero)
                        for replacement in range(4)
                    )
                else:
                    value += sum(
                        GAMMA[current][axis][replacement]
                        * tensor.get(indices[:position] + (replacement,) + indices[position + 1 :], sp.S.Zero)
                        for replacement in range(4)
                    )
            output[(axis, *indices)] = _simp(value)
    return output


def _background_geometry() -> dict[str, object]:
    structure = {(a, b, c): coefficient for a in range(4) for b in range(4) for c, coefficient in _structure(a, b).items()}
    riemann: dict[tuple[int, ...], sp.Expr] = {}
    for target, vector, first, second in product(range(4), repeat=4):
        riemann[(target, vector, first, second)] = _simp(
            sum(
                GAMMA[middle][second][vector] * GAMMA[target][first][middle]
                - GAMMA[middle][first][vector] * GAMMA[target][second][middle]
                - structure.get((first, second, middle), sp.S.Zero) * GAMMA[target][middle][vector]
                for middle in range(4)
            )
        )
    ricci = {
        (first, second): _simp(sum(riemann[(index, first, index, second)] for index in range(4)))
        for first, second in product(range(4), repeat=2)
    }
    scalar = _simp(sum(ETA[first, second] * ricci[(first, second)] for first, second in product(range(4), repeat=2)))
    schouten = {
        (first, second): _simp(sp.Rational(1, 2) * (ricci[(first, second)] - scalar * ETA[first, second] / 6))
        for first, second in product(range(4), repeat=2)
    }
    weyl: dict[tuple[int, ...], sp.Expr] = {}
    for a, b, c, d in product(range(4), repeat=4):
        lowered_riemann = sum(ETA[a, target] * riemann[(target, b, c, d)] for target in range(4))
        weyl[(a, b, c, d)] = _simp(
            lowered_riemann
            - (
                ETA[a, c] * schouten[(d, b)]
                - ETA[a, d] * schouten[(c, b)]
                - ETA[b, c] * schouten[(d, a)]
                + ETA[b, d] * schouten[(c, a)]
            )
        )
    return {
        "riemann": riemann,
        "ricci": ricci,
        "scalar": scalar,
        "schouten": schouten,
        "weyl": weyl,
    }


def _metric_perturbation() -> dict[tuple[int, int], LinearOperator]:
    output: dict[tuple[int, int], LinearOperator] = {}
    for first, second in product(range(4), repeat=2):
        output[(first, second)] = LinearOperator.basis(PAIR_INDEX[tuple(sorted((first, second)))])
    return output


def _linearized_curvature(background: dict[str, object]) -> dict[str, object]:
    h = _metric_perturbation()
    nabla_h = _covariant_derivative_operator(h, (-1, -1))
    delta_gamma: dict[tuple[int, ...], LinearOperator] = {}
    for target, first, second in product(range(4), repeat=3):
        delta_gamma[(target, first, second)] = _sum_ops(
            (
                nabla_h[(first, second, contracted)]
                + nabla_h[(second, first, contracted)]
                - nabla_h[(contracted, first, second)]
            ).scale(ETA[target, contracted] / 2)
            for contracted in range(4)
        )
    derivative_gamma = _covariant_derivative_operator(delta_gamma, (1, -1, -1))
    delta_riemann: dict[tuple[int, ...], LinearOperator] = {}
    for target, vector, first, second in product(range(4), repeat=4):
        delta_riemann[(target, vector, first, second)] = (
            derivative_gamma[(first, target, second, vector)]
            - derivative_gamma[(second, target, first, vector)]
        )
    delta_ricci = {
        (first, second): _sum_ops(
            delta_riemann[(index, first, index, second)] for index in range(4)
        )
        for first, second in product(range(4), repeat=2)
    }
    ricci = background["ricci"]
    scalar = background["scalar"]
    delta_scalar = _sum_ops(
        delta_ricci[(first, second)].scale(ETA[first, second])
        for first, second in product(range(4), repeat=2)
    ) - _sum_ops(
        h[(left, right)].scale(
            ETA[first, left] * ETA[second, right] * ricci[(first, second)]
        )
        for first, second, left, right in product(range(4), repeat=4)
    )
    delta_schouten = {
        (first, second): (
            delta_ricci[(first, second)]
            - delta_scalar.scale(ETA[first, second] / 6)
            - h[(first, second)].scale(scalar / 6)
        ).scale(sp.Rational(1, 2))
        for first, second in product(range(4), repeat=2)
    }
    riemann = background["riemann"]
    schouten = background["schouten"]
    delta_weyl: dict[tuple[int, ...], LinearOperator] = {}
    for a, b, c, d in product(range(4), repeat=4):
        delta_lower_riemann = _sum_ops(
            h[(a, target)].scale(riemann[(target, b, c, d)])
            + delta_riemann[(target, b, c, d)].scale(ETA[a, target])
            for target in range(4)
        )
        delta_g_wedge_p = (
            h[(a, c)].scale(schouten[(d, b)])
            + delta_schouten[(d, b)].scale(ETA[a, c])
            - h[(a, d)].scale(schouten[(c, b)])
            - delta_schouten[(c, b)].scale(ETA[a, d])
            - h[(b, c)].scale(schouten[(d, a)])
            - delta_schouten[(d, a)].scale(ETA[b, c])
            + h[(b, d)].scale(schouten[(c, a)])
            + delta_schouten[(c, a)].scale(ETA[b, d])
        )
        delta_weyl[(a, b, c, d)] = delta_lower_riemann - delta_g_wedge_p
    return {
        "h": h,
        "delta_gamma": delta_gamma,
        "delta_ricci": delta_ricci,
        "delta_scalar": delta_scalar,
        "delta_schouten": delta_schouten,
        "delta_weyl": delta_weyl,
    }


def _linearized_bach(
    background: dict[str, object],
    variation: dict[str, object],
) -> dict[tuple[int, int], LinearOperator]:
    h = variation["h"]
    delta_gamma = variation["delta_gamma"]
    delta_p = variation["delta_schouten"]
    delta_c = variation["delta_weyl"]
    p = background["schouten"]
    c_tensor = background["weyl"]
    dp = _covariant_derivative_background(p, (-1, -1))
    ddp = _covariant_derivative_background(dp, (-1, -1, -1))

    delta_dp: dict[tuple[int, ...], LinearOperator] = {}
    derivative_delta_p = _covariant_derivative_operator(delta_p, (-1, -1))
    for derivative, first, second in product(range(4), repeat=3):
        delta_dp[(derivative, first, second)] = (
            derivative_delta_p[(derivative, first, second)]
            - _sum_ops(delta_gamma[(target, derivative, first)].scale(p[(target, second)]) for target in range(4))
            - _sum_ops(delta_gamma[(target, derivative, second)].scale(p[(first, target)]) for target in range(4))
        )
    derivative_delta_dp = _covariant_derivative_operator(delta_dp, (-1, -1, -1))
    delta_ddp: dict[tuple[int, ...], LinearOperator] = {}
    for outer, inner, first, second in product(range(4), repeat=4):
        delta_ddp[(outer, inner, first, second)] = (
            derivative_delta_dp[(outer, inner, first, second)]
            - _sum_ops(delta_gamma[(target, outer, inner)].scale(dp[(target, first, second)]) for target in range(4))
            - _sum_ops(delta_gamma[(target, outer, first)].scale(dp[(inner, target, second)]) for target in range(4))
            - _sum_ops(delta_gamma[(target, outer, second)].scale(dp[(inner, first, target)]) for target in range(4))
        )

    delta_p_up: dict[tuple[int, int], LinearOperator] = {}
    for first, second in product(range(4), repeat=2):
        value = _sum_ops(
            delta_p[(left, right)].scale(ETA[first, left] * ETA[second, right])
            for left, right in product(range(4), repeat=2)
        )
        value = value - _sum_ops(
            h[(left, right)].scale(
                ETA[first, left] * ETA[contracted, right] * ETA[second, other] * p[(contracted, other)]
            )
            for left, right, contracted, other in product(range(4), repeat=4)
        )
        value = value - _sum_ops(
            h[(left, right)].scale(
                ETA[second, left] * ETA[contracted, right] * ETA[first, other] * p[(other, contracted)]
            )
            for left, right, contracted, other in product(range(4), repeat=4)
        )
        delta_p_up[(first, second)] = value

    p_up = {
        (first, second): _simp(
            sum(ETA[first, left] * ETA[second, right] * p[(left, right)] for left, right in product(range(4), repeat=2))
        )
        for first, second in product(range(4), repeat=2)
    }
    output: dict[tuple[int, int], LinearOperator] = {}
    for first, second in product(range(4), repeat=2):
        laplacian = _sum_ops(
            delta_ddp[(outer, inner, first, second)].scale(ETA[outer, inner])
            for outer, inner in product(range(4), repeat=2)
        ) - _sum_ops(
            h[(left, right)].scale(
                ETA[outer, left] * ETA[inner, right] * ddp[(outer, inner, first, second)]
            )
            for outer, inner, left, right in product(range(4), repeat=4)
        )
        mixed = _sum_ops(
            delta_ddp[(outer, first, second, inner)].scale(ETA[outer, inner])
            for outer, inner in product(range(4), repeat=2)
        ) - _sum_ops(
            h[(left, right)].scale(
                ETA[outer, left] * ETA[inner, right] * ddp[(outer, first, second, inner)]
            )
            for outer, inner, left, right in product(range(4), repeat=4)
        )
        curvature = _sum_ops(
            delta_p_up[(inner, outer)].scale(c_tensor[(first, inner, second, outer)])
            + delta_c[(first, inner, second, outer)].scale(p_up[(inner, outer)])
            for inner, outer in product(range(4), repeat=2)
        )
        output[(first, second)] = laplacian - mixed + curvature
    return output


def _operator_matrix(tensor: dict[tuple[int, int], LinearOperator]) -> list[list[LinearOperator]]:
    weights = _canonical_equation_weights()
    rows: list[list[LinearOperator]] = []
    for row, pair in enumerate(PAIRS):
        operator = tensor[pair].scale(weights[row, row])
        rows.append([
            LinearOperator.from_terms(
                (0, word, coefficient)
                for input_component, word, coefficient in operator.terms
                if input_component == column
            )
            for column in range(10)
        ])
    return rows


def _linearized_matter(
    background: dict[str, object],
    variation: dict[str, object],
) -> dict[tuple[int, int], LinearOperator]:
    """Vary the clock stress at fixed dressed-clock representative."""

    h = variation["h"]
    delta_ricci = variation["delta_ricci"]
    delta_scalar = variation["delta_scalar"]
    scalar = background["scalar"]
    rho_squared = 2 * ALPHA_B * U * (V - 4 * U)
    phase_kinetic = ALPHA_B * U**3 * V / 2
    potential = -ALPHA_B * U**2 * (U**2 - 5 * U * V + V**2) / 6
    delta_stress: dict[tuple[int, int], LinearOperator] = {}
    for first, second in product(range(4), repeat=2):
        delta_einstein = (
            delta_ricci[(first, second)]
            - delta_scalar.scale(ETA[first, second] / 2)
            - h[(first, second)].scale(scalar / 2)
        )
        delta_stress[(first, second)] = (
            h[(first, second)].scale(phase_kinetic / 2 - potential)
            + h[(0, 0)].scale(ETA[first, second] * phase_kinetic / 2)
            + delta_einstein.scale(rho_squared / 6)
        )
    return delta_stress


def _combine_retained_hessian(
    bach: dict[tuple[int, int], LinearOperator],
    matter: dict[tuple[int, int], LinearOperator],
) -> list[list[LinearOperator]]:
    return _operator_matrix(
        {
            pair: bach[pair].scale(ALPHA_B) - matter[pair]
            for pair in product(range(4), repeat=2)
        }
    )


def _spatial_gauge_operator() -> list[LinearOperator]:
    """Full first-order spatial diffeomorphism generator on metric rows."""

    output: list[LinearOperator] = []
    for first, second in PAIRS:
        value = ZERO
        if second != 0:
            value = value + LinearOperator.from_terms(((second - 1, (first,), sp.S.One),))
        if first != 0:
            value = value + LinearOperator.from_terms(((first - 1, (second,), sp.S.One),))
        value = value - _sum_ops(
            LinearOperator.basis(target - 1).scale(GAMMA[target][first][second])
            for target in range(1, 4)
        )
        value = value - _sum_ops(
            LinearOperator.basis(target - 1).scale(GAMMA[target][second][first])
            for target in range(1, 4)
        )
        output.append(value)
    return output


def _compose_matrix_vector(
    matrix: list[list[LinearOperator]],
    vector: list[LinearOperator],
) -> list[LinearOperator]:
    return [
        _sum_ops(matrix[row][column].compose(vector[column]) for column in range(10))
        for row in range(10)
    ]


def _adjoint_scalar(operator: LinearOperator) -> LinearOperator:
    return LinearOperator.from_terms(
        (0, tuple(reversed(word)), (-1) ** len(word) * coefficient)
        for _, word, coefficient in operator.terms
    )


def _formal_adjoint_defect(
    matrix: list[list[LinearOperator]],
) -> list[list[LinearOperator]]:
    return [
        [matrix[row][column] - _adjoint_scalar(matrix[column][row]) for column in range(10)]
        for row in range(10)
    ]


def _split_operator_vector(vector: list[LinearOperator], input_rank: int) -> list[list[LinearOperator]]:
    return [
        [
            LinearOperator.from_terms(
                (0, word, coefficient)
                for component, word, coefficient in vector[row].terms
                if component == column
            )
            for column in range(input_rank)
        ]
        for row in range(len(vector))
    ]


def _adjoint_matrix(matrix: list[list[LinearOperator]], *, sign: int = 1) -> list[list[LinearOperator]]:
    return [
        [_adjoint_scalar(matrix[row][column]).scale(sign) for row in range(len(matrix))]
        for column in range(len(matrix[0]))
    ]


def _compose_matrices(
    outer: list[list[LinearOperator]],
    inner: list[list[LinearOperator]],
) -> list[list[LinearOperator]]:
    if len(outer[0]) != len(inner):
        raise ValueError("operator matrix shape mismatch")
    return [
        [
            _sum_ops(
                outer[row][middle].compose(inner[middle][column])
                for middle in range(len(inner))
            )
            for column in range(len(inner[0]))
        ]
        for row in range(len(outer))
    ]


def _matrix_record(matrix: list[list[LinearOperator]]) -> dict[str, object]:
    entries = []
    for row in range(len(matrix)):
        for column in range(len(matrix[0])):
            if not matrix[row][column].terms:
                continue
            entries.append(
                [
                    row,
                    column,
                    [
                        [
                            [word.count(axis) for axis in range(4)],
                            str(sp.factor(coefficient)),
                        ]
                        for _, word, coefficient in matrix[row][column].terms
                    ],
                ]
            )
    body = {"shape": [len(matrix), len(matrix[0])], "entries": entries}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {**body, "sha256": digest}


def _background_bach(background: dict[str, object]) -> dict[tuple[int, int], sp.Expr]:
    p = background["schouten"]
    c_tensor = background["weyl"]
    dp = _covariant_derivative_background(p, (-1, -1))
    ddp = _covariant_derivative_background(dp, (-1, -1, -1))
    p_up = {
        (first, second): _simp(
            sum(ETA[first, left] * ETA[second, right] * p[(left, right)] for left, right in product(range(4), repeat=2))
        )
        for first, second in product(range(4), repeat=2)
    }
    return {
        (first, second): _simp(
            sum(
                ETA[outer, inner]
                * (
                    ddp[(outer, inner, first, second)]
                    - ddp[(outer, first, second, inner)]
                )
                + p_up[(inner, outer)] * c_tensor[(first, inner, second, outer)]
                for outer, inner in product(range(4), repeat=2)
            )
        )
        for first, second in product(range(4), repeat=2)
    }


def _commutative_symbol(matrix: list[list[LinearOperator]], order: int) -> sp.Matrix:
    momenta = sp.symbols("p0:4")
    return sp.Matrix(
        10,
        10,
        lambda row, column: _simp(
            sum(
                coefficient * sp.prod(momenta[axis] for axis in word)
                for _, word, coefficient in matrix[row][column].by_order(order).terms
            )
        ),
    )


def build_linearized_bach_matrix() -> list[list[LinearOperator]]:
    background = _background_geometry()
    variation = _linearized_curvature(background)
    return _operator_matrix(_linearized_bach(background, variation))


def build_retained_hessian_matrix() -> list[list[LinearOperator]]:
    background = _background_geometry()
    variation = _linearized_curvature(background)
    bach = _linearized_bach(background, variation)
    matter = _linearized_matter(background, variation)
    return _combine_retained_hessian(bach, matter)


@dataclass(frozen=True)
class BergerRetainedMinimalOperator:
    payload: dict[str, object]

    @classmethod
    def build(cls) -> "BergerRetainedMinimalOperator":
        layout = BergerRetainedMinimalLayout.build()
        background = _background_geometry()
        expected_background_bach = {
            (0, 0): (V - U) ** 2 * U**2 / 6,
            (1, 1): U**2 * (V - U) * (V - 3 * U) / 6,
            (2, 2): U**2 * (V - U) * (V - 3 * U) / 6,
            (3, 3): U**2 * (V - U) * (5 * U - V) / 6,
        }
        background_bach = _background_bach(background)
        for pair in product(range(4), repeat=2):
            if _simp(background_bach[pair] - expected_background_bach.get(pair, sp.S.Zero)) != 0:
                raise AssertionError(f"background Bach mismatch at {pair}")

        variation = _linearized_curvature(background)
        bach_tensor = _linearized_bach(background, variation)
        bach = _operator_matrix(bach_tensor)
        retained = _combine_retained_hessian(
            bach_tensor,
            _linearized_matter(background, variation),
        )
        gauge = _split_operator_vector(_spatial_gauge_operator(), 3)
        minus_adjoint = _adjoint_matrix(gauge, sign=-1)

        p = tuple(sp.symbols("p0:4"))
        if sp.simplify(_commutative_symbol(bach, 4) - _principal_geometry(p)["bach"]) != sp.zeros(10):
            raise AssertionError("Berger Bach PBW principal mismatch")
        if any(value.terms for row in _formal_adjoint_defect(retained) for value in row):
            raise AssertionError("retained Hessian is not formally self-adjoint")
        hk = _compose_matrices(retained, gauge)
        kh = _compose_matrices(minus_adjoint, retained)
        if any(value.terms for row in hk for value in row):
            raise AssertionError("H_retained K_spatial is nonzero")
        if any(value.terms for row in kh for value in row):
            raise AssertionError("minus_K_spatial_sharp H_retained is nonzero")

        bach_orders = {
            str(order): sum(
                len(bach[row][column].by_order(order).terms)
                for row, column in product(range(10), repeat=2)
            )
            for order in range(5)
        }
        payload: dict[str, object] = {
            "schema": "pure-weyl-berger-retained-minimal-operator-v1",
            "result_id": "BERGER_RETAINED_MINIMAL_OPERATOR",
            "setting_id": "compact_positive_berger_clock_fixed_coupling_linearized",
            "claim_status": "CERTIFIED_COMPLETE_MINIMAL_Q1",
            "dependency_tags": ["LOCAL-ALGEBRAIC"],
            "layout_ref": {
                "result_id": layout.payload["result_id"],
                "payload_sha256": layout.digest,
                "component_count": 26,
            },
            "coefficient_ring": "Q(alpha_B,u,v)[e0,e1,e2,e3]_PBW with u=c/a^2, v=1/c",
            "pbw_convention": {
                "ordered_words": "e0^n0 e1^n1 e2^n2 e3^n3",
                "commutators": {
                    "[e1,e2]": "u e3",
                    "[e2,e3]": "v e1",
                    "[e3,e1]": "v e2",
                    "[e0,ei]": "0",
                },
                "formal_adjoint": "e_mu^sharp=-e_mu in the unimodular invariant Berger frame",
            },
            "action_inputs": {
                "metric_equation": "alpha_B B_ab-T_ab=0",
                "bach_formula": "B_ab=Box P_ab-nabla^c nabla_a P_bc+P^{cd}C_acbd",
                "clock_action": "int sqrt(-g)[-1/2 sum_A dT_A.dT_A-(R/12)rho^2-(lambda/4)rho^4]",
                "background_substitution": {
                    "a_squared": "1/(u v)",
                    "c_squared": "1/v^2",
                    "q": "u/v",
                    "rho_squared": "2 alpha_B u(v-4u)",
                },
            },
            "q1_blocks": {
                "K_spatial": _matrix_record(gauge),
                "H_retained": _matrix_record(retained),
                "minus_K_spatial_sharp": _matrix_record(minus_adjoint),
            },
            "bach_PBW_term_counts_by_order": bach_orders,
            "exact_checks": {
                "background_Bach_matches_independent_certificate": True,
                "all_Bach_orders_0_through_4_present": all(bach_orders[str(order)] > 0 for order in range(5)),
                "Bach_order4_matches_independent_principal": True,
                "H_retained_formally_self_adjoint": True,
                "H_retained_K_spatial_zero": True,
                "minus_K_spatial_sharp_H_retained_zero": True,
                "q1_retained_squared_zero": True,
                "q1_retained_cyclic": True,
                "all_26_minimal_rows_included": True,
                "support_local": True,
            },
            "flags": {
                "retained_Bach_lower_order_PBW_complete": True,
                "retained_q1_coefficients_complete": True,
                "retained_q1_squared_verified": True,
                "retained_cyclicity_verified": True,
                "BERGER_RETAINED_MINIMAL_OPERATOR": True,
                "BERGER_NONMINIMAL_COMPLETION": False,
                "BERGER_CAUSAL_GREEN_HOMOTOPY": False,
                "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT": False,
            },
            "next_gate": "BERGER_NONMINIMAL_COMPLETION",
            "claim_boundary": "The complete support-local cyclic 26-row minimal q1 is certified coefficientwise. Nonminimal gauge-fixing rows, a causal Green contraction, q2, and the arity-two D-Cartan contraction are not supplied by this result.",
        }
        result = cls(payload)
        result.verify()
        return result

    def verify(self) -> None:
        payload = self.payload
        if payload["layout_ref"]["payload_sha256"] != BergerRetainedMinimalLayout.build().digest:
            raise AssertionError("retained layout reference drifted")
        for record in payload["q1_blocks"].values():
            body = {"shape": record["shape"], "entries": record["entries"]}
            digest = hashlib.sha256(
                json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            if record["sha256"] != digest:
                raise AssertionError("q1 block digest mismatch")
        for key, value in payload["exact_checks"].items():
            if value is not True:
                raise AssertionError(f"exact retained check dropped: {key}")
        flags = payload["flags"]
        for key in (
            "retained_Bach_lower_order_PBW_complete",
            "retained_q1_coefficients_complete",
            "retained_q1_squared_verified",
            "retained_cyclicity_verified",
            "BERGER_RETAINED_MINIMAL_OPERATOR",
        ):
            if flags[key] is not True:
                raise AssertionError(f"proved retained flag dropped: {key}")
        for key in (
            "BERGER_NONMINIMAL_COMPLETION",
            "BERGER_CAUSAL_GREEN_HOMOTOPY",
            "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT",
        ):
            if flags[key] is not False:
                raise AssertionError(f"downstream flag promoted: {key}")
        if payload["next_gate"] != "BERGER_NONMINIMAL_COMPLETION":
            raise AssertionError("retained next gate drifted")

    def certificate_text(self) -> str:
        return json.dumps(self.payload, indent=2, sort_keys=True) + "\n"

    def report_text(self) -> str:
        return """# Complete retained Berger minimal BV operator

The full 26-row minimal differential is now coefficientwise exact in the
ordered invariant-frame PBW basis.  It contains the spatial diffeomorphism
generator, the action-derived matter-coupled Berger Hessian, and the cyclic
dual identity row.

The curved Bach block was derived from the Schouten formula on the actual
nonzero-Weyl Berger background.  Its expansion has nonzero terms at every
differential order from zero through four.  The order-four block agrees with
the independently derived principal matrix, while the background formula
reproduces the separately certified Berger Bach tensor.

Exact PBW composition proves

```text
H_retained K_spatial = 0
minus_K_spatial_sharp H_retained = 0
H_retained^sharp = H_retained
q1_retained^2 = 0
```

All entries are finite-order differential operators with invariant
coefficients and therefore preserve support.  This promotes
`BERGER_RETAINED_MINIMAL_OPERATOR` only.  Nonminimal gauge-fixing rows and the
causal Green contraction remain the next analytic work; q2 and the arity-two
D-Cartan contraction remain downstream.
"""


def _write_result(result: BergerRetainedMinimalOperator) -> None:
    CERTIFICATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    CERTIFICATE_PATH.write_text(result.certificate_text())
    REPORT_PATH.write_text(result.report_text())


def _check_result(result: BergerRetainedMinimalOperator) -> None:
    if CERTIFICATE_PATH.read_text() != result.certificate_text():
        raise AssertionError("retained operator certificate drifted")
    if REPORT_PATH.read_text() != result.report_text():
        raise AssertionError("retained operator report drifted")


def _mutation_guards(result: BergerRetainedMinimalOperator) -> None:
    mutations = [
        ("drop q1 square", ("exact_checks", "q1_retained_squared_zero"), False),
        ("drop cyclicity", ("flags", "retained_cyclicity_verified"), False),
        ("promote nonminimal", ("flags", "BERGER_NONMINIMAL_COMPLETION"), True),
        ("promote causal", ("flags", "BERGER_CAUSAL_GREEN_HOMOTOPY"), True),
        ("promote q2 export", ("flags", "CLASSICAL_SUPPORT_LOCAL_Q1_Q2_EXPORT"), True),
        ("skip nonminimal", ("next_gate",), "BERGER_CAUSAL_GREEN_HOMOTOPY"),
    ]
    for name, path, value in mutations:
        payload = deepcopy(result.payload)
        target = payload
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            BergerRetainedMinimalOperator(payload).verify()
        except AssertionError:
            continue
        raise AssertionError(f"mutation guard failed: {name}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--guards", action="store_true")
    args = parser.parse_args()
    result = BergerRetainedMinimalOperator.build()
    if args.check:
        _check_result(result)
    else:
        _write_result(result)
    if args.guards:
        _mutation_guards(result)
    print("BERGER_RETAINED_MINIMAL_OPERATOR: PASS")
    print(f"Bach PBW term counts by order: {result.payload['bach_PBW_term_counts_by_order']}")
    print("complete 26-row minimal q1, nilpotency, and cyclicity: PASS")
    print("nonminimal and causal gates: OPEN")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
