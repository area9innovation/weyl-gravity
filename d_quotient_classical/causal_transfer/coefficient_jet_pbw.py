"""Associative first-variation PBW composition with coefficient jets.

``FirstVariationPBW`` differentiates curvature-dependent PBW rewriting, but
its historical ``(base, delta)`` operator type stores only the value of the
varied normal-form coefficients at one point.  That is insufficient when an
outer derivative hits a varied coefficient produced by an earlier
composition.

This module keeps a callable covariant jet tower for every varied
coefficient.  It assumes that the *base* normal-form coefficients are
parallel, as they are in the locally symmetric Nariai calculation.  The
variation may be nonparallel.  Composition then applies the covariant
Leibniz rule before PBW-normalizing the derivatives which still hit the
field.  Curvature-rewrite coefficients use the independently supplied
curvature jets from :mod:`first_variation_pbw`.

The representation is intentionally lazy: a composite requests only the
coefficient jets actually needed by a downstream calculation.  This makes
missing geometric input explicit instead of silently replacing it by zero.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from itertools import combinations
from typing import Callable, Mapping

import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    OperatorTable,
    _add,
    _clean,
)
from d_quotient_classical.causal_transfer.first_variation_pbw import (
    FirstVariationPBW,
)


CoefficientJet = Callable[[tuple[int, ...]], OperatorTable]


def _add_safe(*tables: Mapping[tuple[int, ...], sp.Matrix]) -> OperatorTable:
    values = tuple(table for table in tables if table)
    return _add(*values) if values else {}


class MissingCoefficientJet(RuntimeError):
    """Raised when point data are used where a positive-order jet is needed."""

    def __init__(self, operator: str, word: tuple[int, ...]) -> None:
        super().__init__(f"missing coefficient jet for {operator}: {word}")
        self.operator = operator
        self.word = word


@dataclass
class JetLinearizedOperator:
    """A base operator and the covariant jet tower of its first variation."""

    base: OperatorTable
    coefficient_jet: CoefficientJet
    name: str
    requested_words: set[tuple[int, ...]] = field(default_factory=set)

    def delta(self, word: tuple[int, ...] = ()) -> OperatorTable:
        word = tuple(word)
        self.requested_words.add(word)
        return self.coefficient_jet(word)


def parallel_zero_variation(
    table: Mapping[tuple[int, ...], sp.Matrix], name: str
) -> JetLinearizedOperator:
    return JetLinearizedOperator(dict(table), lambda _word: {}, name)


def point_value_only(
    table: Mapping[tuple[int, ...], sp.Matrix],
    delta_value: Mapping[tuple[int, ...], sp.Matrix],
    name: str,
) -> JetLinearizedOperator:
    """Create a fail-closed operator when only the zeroth coefficient jet exists."""

    value = dict(delta_value)

    def provider(word: tuple[int, ...]) -> OperatorTable:
        if word:
            raise MissingCoefficientJet(name, word)
        return value

    return JetLinearizedOperator(dict(table), provider, name)


def jet_add(
    *operators: JetLinearizedOperator, name: str = "sum"
) -> JetLinearizedOperator:
    if not operators:
        raise ValueError("jet_add requires at least one operator")

    @lru_cache(maxsize=None)
    def provider(word: tuple[int, ...]) -> OperatorTable:
        return _add_safe(*(operator.delta(word) for operator in operators))

    return JetLinearizedOperator(
        _add_safe(*(operator.base for operator in operators)), provider, name
    )


def jet_scale(
    operator: JetLinearizedOperator, scalar: sp.Expr, name: str | None = None
) -> JetLinearizedOperator:
    def scale(table: Mapping[tuple[int, ...], sp.Matrix]) -> OperatorTable:
        return _clean({word: scalar * matrix for word, matrix in table.items()})

    @lru_cache(maxsize=None)
    def provider(word: tuple[int, ...]) -> OperatorTable:
        return scale(operator.delta(word))

    return JetLinearizedOperator(
        scale(operator.base), provider, name or f"{scalar}*{operator.name}"
    )


class CoefficientJetPBW:
    """PBW composition retaining all first-order coefficient jets.

    The wrapped :class:`FirstVariationPBW` supplies the base PBW algebra and
    the varied curvature jets.  This class adds the missing Leibniz terms in
    which outer derivatives hit varied operator coefficients.
    """

    def __init__(self, linearized_pbw: FirstVariationPBW) -> None:
        self.linearized_pbw = linearized_pbw
        self.base = linearized_pbw.base
        self.name = linearized_pbw.name
        self._delta_canonical_cache: dict[
            tuple[tuple[int, ...], int, tuple[int, ...]],
            dict[tuple[tuple[int, ...], int], sp.Expr],
        ] = {}

    def _delta_canonical_term(
        self,
        word: tuple[int, ...],
        component: int,
        external_jet: tuple[int, ...],
    ) -> dict[tuple[tuple[int, ...], int], sp.Expr]:
        """PBW variation with an external derivative on its coefficient."""

        key = (word, component, external_jet)
        if key in self._delta_canonical_cache:
            return self._delta_canonical_cache[key]
        inversion = next(
            (
                index
                for index in range(len(word) - 1)
                if word[index] > word[index + 1]
            ),
            None,
        )
        if inversion is None:
            self._delta_canonical_cache[key] = {}
            return {}

        position = inversion
        left, right = word[position], word[position + 1]
        prefix = word[:position]
        suffix = word[position + 2 :]
        swapped = word[:position] + (right, left) + suffix
        result: dict[tuple[tuple[int, ...], int], sp.Expr] = defaultdict(
            lambda: sp.Integer(0)
        )

        for changed, coefficient in self._delta_canonical_term(
            swapped, component, external_jet
        ).items():
            result[changed] += coefficient

        for (changed_suffix, changed_component), curvature_coefficient in (
            self.base._curvature_action(left, right, suffix, component).items()
        ):
            shortened = prefix + changed_suffix
            for changed, coefficient in self._delta_canonical_term(
                shortened, changed_component, external_jet
            ).items():
                result[changed] += curvature_coefficient * coefficient

        positions = tuple(range(len(prefix)))
        for count in range(len(prefix) + 1):
            for selected in combinations(positions, count):
                selected_set = set(selected)
                internal_jet = tuple(prefix[index] for index in selected)
                remaining = tuple(
                    axis
                    for index, axis in enumerate(prefix)
                    if index not in selected_set
                )
                for (changed_suffix, changed_component), varied_coefficient in (
                    self.linearized_pbw._delta_curvature_action(
                        left,
                        right,
                        suffix,
                        component,
                        external_jet + internal_jet,
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
        self._delta_canonical_cache[key] = output
        return output

    def _curvature_variation_jet(
        self,
        outer: Mapping[tuple[int, ...], sp.Matrix],
        inner: Mapping[tuple[int, ...], sp.Matrix],
        external_jet: tuple[int, ...],
    ) -> OperatorTable:
        if not outer or not inner:
            return {}
        output_rank = next(iter(outer.values())).rows
        result: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(output_rank, self.base.rank)
        )
        inner_by_row: dict[
            tuple[int, ...], dict[int, list[tuple[int, sp.Expr]]]
        ] = {}
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
                            self._delta_canonical_term(
                                outer_word + inner_word,
                                component,
                                external_jet,
                            ).items()
                        ):
                            result[changed_word][row, changed_component] += (
                                left_value * right_value * coefficient
                            )
        return _clean(result)

    def _base_outer_on_delta_inner(
        self,
        outer: Mapping[tuple[int, ...], sp.Matrix],
        inner: JetLinearizedOperator,
        external_jet: tuple[int, ...],
    ) -> OperatorTable:
        if not outer:
            return {}
        output_rank = next(iter(outer.values())).rows
        raw: dict[tuple[int, ...], sp.Matrix] = defaultdict(
            lambda: sp.zeros(output_rank, self.base.rank)
        )
        for outer_word, outer_matrix in outer.items():
            positions = tuple(range(len(outer_word)))
            for count in range(len(outer_word) + 1):
                for selected in combinations(positions, count):
                    selected_set = set(selected)
                    coefficient_word = tuple(
                        outer_word[index] for index in selected
                    )
                    field_word = tuple(
                        axis
                        for index, axis in enumerate(outer_word)
                        if index not in selected_set
                    )
                    for inner_word, inner_matrix in inner.delta(
                        external_jet + coefficient_word
                    ).items():
                        raw[field_word + inner_word] += outer_matrix * inner_matrix
        return self.base.canonicalize_table(raw)

    def compose(
        self,
        outer: JetLinearizedOperator,
        inner: JetLinearizedOperator,
        name: str | None = None,
    ) -> JetLinearizedOperator:
        base = self.base.compose(outer.base, inner.base)

        @lru_cache(maxsize=None)
        def provider(external_jet: tuple[int, ...]) -> OperatorTable:
            return _add_safe(
                # External derivatives hit the unique varied outer
                # coefficient; the inner base coefficients are parallel.
                self.base.compose(outer.delta(external_jet), inner.base),
                # Outer base derivatives distribute between the varied inner
                # coefficient and the field by the covariant Leibniz rule.
                self._base_outer_on_delta_inner(
                    outer.base, inner, external_jet
                ),
                # The unique variation may instead be the curvature used by
                # PBW normal ordering of the base composition.
                self._curvature_variation_jet(
                    outer.base, inner.base, external_jet
                ),
            )

        return JetLinearizedOperator(
            base,
            provider,
            name or f"({outer.name})o({inner.name})",
        )
