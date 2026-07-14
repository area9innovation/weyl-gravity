"""Small exact-index engine for the unit-sphere curl certificates."""

from __future__ import annotations

from collections.abc import Iterable

import sympy as sp


DIMENSION = 3


def delta(first: int, second: int) -> sp.Integer:
    return sp.Integer(first == second)


def epsilon(first: int, second: int, third: int) -> sp.Expr:
    return sp.LeviCivita(first, second, third)


def sphere_curvature(
    first: int, second: int, covector: int, raised: int
) -> sp.Expr:
    """Return ``R_(first second covector)^raised`` in repository convention.

    The convention is fixed by

    ``[D^n,D_i] v_n=2v_i`` and
    ``[D^n,D_i] h_(nj)=3h_(ij)`` for trace-free symmetric ``h``.
    """

    return (
        delta(second, raised) * delta(first, covector)
        - delta(first, raised) * delta(second, covector)
    )


def rowspace_contains(
    constraints: Iterable[sp.Expr], expression: sp.Expr, variables: Iterable[sp.Symbol]
) -> bool:
    """Test exact equality modulo homogeneous linear constraints."""

    variables = tuple(variables)
    matrix, _ = sp.linear_eq_to_matrix(tuple(constraints), variables)
    row, _ = sp.linear_eq_to_matrix((sp.expand(expression),), variables)
    return matrix.col_join(row).rank() == matrix.rank()


def symmetric_symbols(prefix: str) -> tuple[dict[tuple[int, int], sp.Symbol], tuple[sp.Symbol, ...]]:
    values: dict[tuple[int, int], sp.Symbol] = {}
    independent: list[sp.Symbol] = []
    for first in range(DIMENSION):
        for second in range(first, DIMENSION):
            symbol = sp.Symbol(f"{prefix}{first}{second}")
            values[first, second] = symbol
            values[second, first] = symbol
            independent.append(symbol)
    return values, tuple(independent)
