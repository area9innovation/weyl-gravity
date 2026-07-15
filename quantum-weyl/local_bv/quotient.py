"""Exact deterministic quotients by tensor and total-derivative relations."""

from __future__ import annotations

from fractions import Fraction
from typing import Iterable, Sequence

from .tensors import TensorExpression, TensorMonomial


def _rref(
    rows: Sequence[Sequence[Fraction]],
) -> tuple[list[list[Fraction]], tuple[int, ...]]:
    matrix = [list(map(Fraction, row)) for row in rows if any(row)]
    if not matrix:
        return [], ()
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise ValueError("relation matrix is ragged")
    pivot_row = 0
    pivots: list[int] = []
    for column in range(width):
        source = next(
            (row for row in range(pivot_row, len(matrix)) if matrix[row][column]),
            None,
        )
        if source is None:
            continue
        matrix[pivot_row], matrix[source] = matrix[source], matrix[pivot_row]
        pivot = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            coefficient = matrix[row][column]
            matrix[row] = [
                value - coefficient * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    # Dependent input relations reduce to trailing zero rows.  Excluding them
    # keeps the stored RREF itself a rank-sized proof object, which matters for
    # large generated relation sets and their machine certificates.
    return matrix[:pivot_row], tuple(pivots)


def exact_rank(rows: Sequence[Sequence[Fraction]]) -> int:
    return len(_rref(rows)[1])


def exact_nullspace(
    rows: Sequence[Sequence[Fraction | int]],
    *,
    column_count: int | None = None,
) -> tuple[tuple[Fraction, ...], ...]:
    """Return a deterministic exact basis for the right nullspace.

    ``column_count`` is required only for an empty matrix, where the number of
    columns cannot otherwise be inferred. Free columns are visited in their
    ambient order, so the resulting basis is stable across hash seeds.
    """

    if rows:
        inferred = len(rows[0])
        if any(len(row) != inferred for row in rows):
            raise ValueError("matrix is ragged")
        if column_count is not None and column_count != inferred:
            raise ValueError("declared column count disagrees with matrix")
        width = inferred
    elif column_count is not None:
        width = column_count
    else:
        raise ValueError("column_count is required for an empty matrix")
    if width < 0:
        raise ValueError("column_count must be nonnegative")

    rref, pivots = _rref(rows)
    free_columns = tuple(column for column in range(width) if column not in pivots)
    basis: list[tuple[Fraction, ...]] = []
    for free in free_columns:
        vector = [Fraction() for _ in range(width)]
        vector[free] = Fraction(1)
        for row, pivot in zip(rref, pivots):
            vector[pivot] = -row[free]
        basis.append(tuple(vector))
    return tuple(basis)


class RelationQuotient:
    """A finite exact vector-space quotient with deterministic normal forms."""

    def __init__(
        self,
        basis: Iterable[TensorMonomial],
        relations: Iterable[TensorExpression],
    ) -> None:
        canonical_basis: set[TensorMonomial] = set()
        for monomial in basis:
            sign, canonical = monomial.canonicalize()
            if sign and canonical is not None:
                canonical_basis.add(canonical)
        self.basis = tuple(sorted(canonical_basis, key=TensorMonomial.sort_key))
        self.position = {monomial: index for index, monomial in enumerate(self.basis)}
        relation_rows = [self.vector(relation) for relation in relations if relation]
        self.rref, self.pivots = _rref(relation_rows)
        self.free_columns = tuple(
            column for column in range(len(self.basis)) if column not in self.pivots
        )

    @property
    def relation_rank(self) -> int:
        return len(self.pivots)

    @property
    def quotient_dimension(self) -> int:
        return len(self.free_columns)

    def vector(self, expression: TensorExpression) -> list[Fraction]:
        vector = [Fraction() for _ in self.basis]
        for monomial, coefficient in expression.terms.items():
            if monomial not in self.position:
                raise ValueError("expression contains a monomial outside the quotient basis")
            vector[self.position[monomial]] += coefficient
        return vector

    def reduce_vector(self, vector: Sequence[Fraction | int]) -> tuple[Fraction, ...]:
        if len(vector) != len(self.basis):
            raise ValueError("coordinate vector has the wrong dimension")
        reduced = list(map(Fraction, vector))
        for row, pivot in zip(self.rref, self.pivots):
            coefficient = reduced[pivot]
            if coefficient:
                reduced = [
                    value - coefficient * relation_value
                    for value, relation_value in zip(reduced, row)
                ]
        return tuple(reduced)

    def reduce(self, expression: TensorExpression) -> tuple[Fraction, ...]:
        return self.reduce_vector(self.vector(expression))

    def free_coordinates(self, expression: TensorExpression) -> tuple[Fraction, ...]:
        reduced = self.reduce(expression)
        return tuple(reduced[column] for column in self.free_columns)

    def rank_of_classes(self, expressions: Iterable[TensorExpression]) -> int:
        return exact_rank([self.free_coordinates(expression) for expression in expressions])
