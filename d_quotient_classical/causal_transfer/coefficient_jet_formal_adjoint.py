"""Formal adjoints for coefficient-jet PBW operators.

The point-only linearized adjoint used by the historical transverse replay
reversed derivative words after normal ordering.  That is insufficient for a
varied operator whose normal-form coefficients are not parallel: integration
by parts also differentiates those coefficients.  This module expands that
Leibniz rule before PBW normal ordering and retains the complete covariant jet
tower of the resulting adjoint coefficients.

The source and target fibre pairings are assumed parallel with zero first
variation.  That hypothesis is certified for the moving orthonormal
tractor/Hom frame used by the Nariai calculation.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from itertools import combinations
from typing import Mapping

import sympy as sp

from covariant_completion.curved_operator.adjoint_tractor_bgg_curved_pbw import (
    OperatorTable,
    _add,
    _clean,
)
from d_quotient_classical.causal_transfer.coefficient_jet_pbw import (
    CoefficientJetPBW,
    JetLinearizedOperator,
)


def _add_safe(*tables: Mapping[tuple[int, ...], sp.Matrix]) -> OperatorTable:
    values = tuple(table for table in tables if table)
    return _add(*values) if values else {}


def _transform(
    matrix: sp.Matrix,
    source_pairing_inverse: sp.Matrix,
    target_pairing: sp.Matrix,
    sign: int,
) -> sp.Matrix:
    return (
        sign * source_pairing_inverse * matrix.T * target_pairing
    ).applyfunc(sp.expand)


def _canonicalization_variation(
    raw: Mapping[tuple[int, ...], sp.Matrix],
    pbw: CoefficientJetPBW,
    external_jet: tuple[int, ...],
) -> OperatorTable:
    """Vary only the curvature used to PBW-normalize ``raw``."""

    if not raw:
        return {}
    output_rank = next(iter(raw.values())).rows
    result: dict[tuple[int, ...], sp.Matrix] = defaultdict(
        lambda: sp.zeros(output_rank, pbw.base.rank)
    )
    for word, matrix in raw.items():
        for (row, component), value in matrix.todok().items():
            for (changed_word, changed_component), coefficient in (
                pbw._delta_canonical_term(word, component, external_jet).items()
            ):
                result[changed_word][row, changed_component] += value * coefficient
    return _clean(result)


def formal_adjoint(
    operator: JetLinearizedOperator,
    source_pairing: sp.Matrix,
    target_pairing: sp.Matrix,
    target_pbw: CoefficientJetPBW,
    name: str | None = None,
) -> JetLinearizedOperator:
    """Return the coefficient-jet formal adjoint of ``operator``.

    ``operator`` maps the source bundle to the target bundle.  The returned
    operator maps target to source, so PBW normalization is performed in the
    original target bundle.  Pairings must be parallel and unvaried.
    """

    source_inverse = source_pairing.inv()
    raw_base = {
        tuple(reversed(word)): _transform(
            matrix, source_inverse, target_pairing, (-1) ** len(word)
        )
        for word, matrix in operator.base.items()
    }
    base = target_pbw.base.canonicalize_table(raw_base)

    # Differential support is allowed to shrink under variation, but not to
    # acquire undeclared derivative words.  This makes the lazy reconstruction
    # fail closed instead of silently omitting a new varied principal term.
    support = set(operator.base) | set(operator.delta(()))

    @lru_cache(maxsize=None)
    def provider(external_jet: tuple[int, ...]) -> OperatorTable:
        coefficient_terms: list[OperatorTable] = []
        for word in sorted(support):
            reversed_word = tuple(reversed(word))
            positions = tuple(range(len(reversed_word)))
            sign = (-1) ** len(word)
            for count in range(len(positions) + 1):
                for selected in combinations(positions, count):
                    chosen = set(selected)
                    coefficient_word = tuple(
                        reversed_word[index] for index in selected
                    )
                    field_word = tuple(
                        axis
                        for index, axis in enumerate(reversed_word)
                        if index not in chosen
                    )
                    varied = operator.delta(external_jet + coefficient_word)
                    undeclared = set(varied) - support
                    if undeclared:
                        raise RuntimeError(
                            f"formal-adjoint derivative support changed for "
                            f"{operator.name}: {sorted(undeclared)}"
                        )
                    matrix = varied.get(word)
                    if matrix is None:
                        continue
                    transformed = _transform(
                        matrix, source_inverse, target_pairing, sign
                    )
                    coefficient_terms.append(
                        target_pbw.base.canonicalize_table(
                            {field_word: transformed}
                        )
                    )
        return _add_safe(
            *coefficient_terms,
            _canonicalization_variation(raw_base, target_pbw, external_jet),
        )

    return JetLinearizedOperator(
        base,
        provider,
        name or f"({operator.name})^sharp",
    )

