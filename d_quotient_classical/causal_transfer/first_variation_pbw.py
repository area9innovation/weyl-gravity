"""First variation of PBW normal ordering about a parallel-curvature base.

The base ``FibrePBW`` algebra assumes parallel curvature.  This module keeps
that exact base normal form and differentiates its rewrite rule when the
curvature variation has prescribed covariant jets.  It is intentionally
linear in the perturbation: precisely one varied curvature (or one of its
jets) occurs in every new term.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations
from typing import Callable, Mapping

import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    FibrePBW,
    OperatorTable,
    _add,
    _clean,
)


Curvature = tuple[tuple[sp.Matrix, ...], ...]
CovectorCurvature = tuple[tuple[sp.Matrix, ...], ...]
JetFactor = Callable[[tuple[int, ...]], sp.Expr]
CurvatureJet = Callable[[int, int, tuple[int, ...]], sp.Matrix]
LinearizedOperator = tuple[OperatorTable, OperatorTable]


def _add_safe(*tables: Mapping[tuple[int, ...], sp.Matrix]) -> OperatorTable:
    values = tuple(table for table in tables if table)
    return _add(*values) if values else {}


def zero_variation(table: Mapping[tuple[int, ...], sp.Matrix]) -> LinearizedOperator:
    return dict(table), {}


def lin_add(*operators: LinearizedOperator) -> LinearizedOperator:
    return _add_safe(*(operator[0] for operator in operators)), _add_safe(
        *(operator[1] for operator in operators)
    )


def lin_scale(operator: LinearizedOperator, scalar: sp.Expr) -> LinearizedOperator:
    return (
        _clean({word: scalar * matrix for word, matrix in operator[0].items()}),
        _clean({word: scalar * matrix for word, matrix in operator[1].items()}),
    )


class FirstVariationPBW:
    """Differentiate PBW canonicalization for one input representation."""

    def __init__(
        self,
        base: FibrePBW,
        delta_fibre_curvature: Curvature,
        delta_covector_curvature: CovectorCurvature,
        jet_factor: JetFactor,
        name: str,
        delta_fibre_jet: CurvatureJet | None = None,
        delta_covector_jet: CurvatureJet | None = None,
    ) -> None:
        self.base = base
        self.delta_fibre_curvature = delta_fibre_curvature
        self.delta_covector_curvature = delta_covector_curvature
        self.jet_factor = jet_factor
        self.name = name
        self.delta_fibre_jet = delta_fibre_jet
        self.delta_covector_jet = delta_covector_jet
        self.rank = base.rank
        self.requested_jet_words: set[tuple[int, ...]] = set()
        self._cache: dict[
            tuple[tuple[int, ...], int],
            dict[tuple[tuple[int, ...], int], sp.Expr],
        ] = {}

    def _delta_curvature_action(
        self,
        left: int,
        right: int,
        derivative_suffix: tuple[int, ...],
        component: int,
        jet_word: tuple[int, ...],
    ) -> dict[tuple[tuple[int, ...], int], sp.Expr]:
        factor = self.jet_factor(jet_word)
        self.requested_jet_words.add(jet_word)
        result: dict[tuple[tuple[int, ...], int], sp.Expr] = defaultdict(
            lambda: sp.Integer(0)
        )
        covector = (
            self.delta_covector_jet(left, right, jet_word)
            if self.delta_covector_jet is not None
            else factor * self.delta_covector_curvature[left][right]
        )
        for position, old_axis in enumerate(derivative_suffix):
            for new_axis in range(4):
                coefficient = covector[old_axis, new_axis]
                if coefficient == 0:
                    continue
                changed = list(derivative_suffix)
                changed[position] = new_axis
                result[(tuple(changed), component)] += coefficient
        fibre = (
            self.delta_fibre_jet(left, right, jet_word)
            if self.delta_fibre_jet is not None
            else factor * self.delta_fibre_curvature[left][right]
        )
        for new_component in range(self.rank):
            coefficient = fibre[component, new_component]
            if coefficient != 0:
                result[(derivative_suffix, new_component)] += coefficient
        return {
            key: sp.expand(value)
            for key, value in result.items()
            if sp.expand(value) != 0
        }

    def delta_canonical_term(
        self, word: tuple[int, ...], component: int
    ) -> dict[tuple[tuple[int, ...], int], sp.Expr]:
        """First variation of ``base.canonical_term(word, component)``."""

        key = (word, component)
        if key in self._cache:
            return self._cache[key]
        inversion = next(
            (
                index
                for index in range(len(word) - 1)
                if word[index] > word[index + 1]
            ),
            None,
        )
        if inversion is None:
            self._cache[key] = {}
            return {}

        position = inversion
        left, right = word[position], word[position + 1]
        prefix = word[:position]
        suffix = word[position + 2 :]
        swapped = word[:position] + (right, left) + suffix
        result: dict[tuple[tuple[int, ...], int], sp.Expr] = defaultdict(
            lambda: sp.Integer(0)
        )

        # Variation of the recursively normal-ordered swapped word.
        for changed, coefficient in self.delta_canonical_term(swapped, component).items():
            result[changed] += coefficient

        # A base curvature commutator followed by a varied rewrite later in
        # the shortened derivative word.
        for (changed_suffix, changed_component), curvature_coefficient in (
            self.base._curvature_action(left, right, suffix, component).items()
        ):
            shortened = prefix + changed_suffix
            for changed, coefficient in self.delta_canonical_term(
                shortened, changed_component
            ).items():
                result[changed] += curvature_coefficient * coefficient

        # The varied curvature and every covariant Leibniz jet produced when
        # some prefix derivatives land on it.  Only jet words accepted by
        # ``jet_factor`` contribute; no assumption about the accepted axes is
        # hard-coded here.
        prefix_positions = tuple(range(len(prefix)))
        for count in range(len(prefix) + 1):
            for selected in combinations(prefix_positions, count):
                selected_set = set(selected)
                jet_word = tuple(prefix[index] for index in selected)
                remaining = tuple(
                    axis for index, axis in enumerate(prefix) if index not in selected_set
                )
                for (changed_suffix, changed_component), varied_coefficient in (
                    self._delta_curvature_action(
                        left, right, suffix, component, jet_word
                    ).items()
                ):
                    shortened = remaining + changed_suffix
                    for changed, coefficient in self.base.canonical_term(
                        shortened, changed_component
                    ).items():
                        result[changed] += varied_coefficient * coefficient

        output = {
            changed: sp.expand(coefficient)
            for changed, coefficient in result.items()
            if sp.expand(coefficient) != 0
        }
        self._cache[key] = output
        return output

    def canonicalize_variation(
        self, table: Mapping[tuple[int, ...], sp.Matrix]
    ) -> OperatorTable:
        if not table:
            return {}
        sample = next(iter(table.values()))
        result: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(sample.rows, self.rank)
        )
        for word, matrix in table.items():
            if matrix.cols != self.rank:
                raise AssertionError(
                    f"{self.name} PBW input rank mismatch: {matrix.cols}!={self.rank}"
                )
            for (row, component), value in matrix.todok().items():
                for (changed_word, changed_component), coefficient in (
                    self.delta_canonical_term(word, component).items()
                ):
                    result[changed_word][row, changed_component] += value * coefficient
        return _clean(result)

    def canonicalize_linearized(
        self,
        base_table: Mapping[tuple[int, ...], sp.Matrix],
        delta_table: Mapping[tuple[int, ...], sp.Matrix],
    ) -> LinearizedOperator:
        base = self.base.canonicalize_table(base_table)
        delta = _add_safe(
            self.base.canonicalize_table(delta_table),
            self.canonicalize_variation(base_table),
        )
        return base, delta

    def _composition_pbw_variation(
        self,
        outer: Mapping[tuple[int, ...], sp.Matrix],
        inner: Mapping[tuple[int, ...], sp.Matrix],
    ) -> OperatorTable:
        if not outer or not inner:
            return {}
        output_rank = next(iter(outer.values())).rows
        result: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(output_rank, self.rank)
        )
        inner_by_row: dict[tuple[int, ...], dict[int, list[tuple[int, sp.Expr]]]] = {}
        for inner_word, inner_matrix in inner.items():
            rows: dict[int, list[tuple[int, sp.Expr]]] = defaultdict(list)
            for (middle, component), value in inner_matrix.todok().items():
                rows[middle].append((component, value))
            inner_by_row[inner_word] = rows
        for outer_word, outer_matrix in outer.items():
            for (row, middle), left_value in outer_matrix.todok().items():
                for inner_word, rows in inner_by_row.items():
                    for component, right_value in rows.get(middle, ()):
                        for (changed_word, changed_component), coefficient in (
                            self.delta_canonical_term(
                                outer_word + inner_word, component
                            ).items()
                        ):
                            result[changed_word][row, changed_component] += (
                                left_value * right_value * coefficient
                            )
        return _clean(result)

    def compose(
        self,
        outer: LinearizedOperator,
        inner: LinearizedOperator,
    ) -> LinearizedOperator:
        base = self.base.compose(outer[0], inner[0])
        delta = _add_safe(
            self.base.compose(outer[1], inner[0]),
            self.base.compose(outer[0], inner[1]),
            self._composition_pbw_variation(outer[0], inner[0]),
        )
        return base, delta

    def formal_adjoint(
        self,
        table: LinearizedOperator,
        source_pairing: sp.Matrix,
        target_pairing: sp.Matrix,
    ) -> LinearizedOperator:
        def raw(value: Mapping[tuple[int, ...], sp.Matrix]) -> OperatorTable:
            return {
                tuple(reversed(word)): (
                    (-1) ** len(word)
                    * source_pairing.inv()
                    * matrix.T
                    * target_pairing
                ).applyfunc(sp.expand)
                for word, matrix in value.items()
            }

        return self.canonicalize_linearized(raw(table[0]), raw(table[1]))
