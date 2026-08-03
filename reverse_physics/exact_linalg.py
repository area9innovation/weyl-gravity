"""Exact rational linear algebra for the reverse-physics carriers.

Deliberately dependency-free and float-free: every entry is a
``fractions.Fraction`` and every rank is computed by exact elimination.  Rail A
(the generator) uses :func:`rank_fraction`; rail B (the verifier) uses the
fraction-free integer Bareiss routine :func:`rank_bareiss` so that the two rails
do not share an elimination implementation.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Sequence

Matrix = list[list[Fraction]]


def to_fraction_matrix(rows: Sequence[Sequence[object]]) -> Matrix:
    return [[Fraction(entry) for entry in row] for row in rows]


def rank_fraction(rows: Sequence[Sequence[object]]) -> int:
    """Rank by Gauss--Jordan elimination over Q (rail A)."""
    matrix = to_fraction_matrix(rows)
    if not matrix:
        return 0
    width = len(matrix[0])
    rank = 0
    for column in range(width):
        pivot = None
        for index in range(rank, len(matrix)):
            if matrix[index][column] != 0:
                pivot = index
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scale = matrix[rank][column]
        matrix[rank] = [entry / scale for entry in matrix[rank]]
        for index in range(len(matrix)):
            if index != rank and matrix[index][column] != 0:
                factor = matrix[index][column]
                matrix[index] = [
                    a - factor * b for a, b in zip(matrix[index], matrix[rank])
                ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def rank_bareiss(rows: Sequence[Sequence[object]]) -> int:
    """Rank by fraction-free Bareiss elimination over Z (rail B).

    Denominators are cleared row by row first, so the elimination never leaves
    the integers and never divides inexactly.
    """
    cleared: list[list[int]] = []
    for row in rows:
        fractions = [Fraction(entry) for entry in row]
        multiplier = 1
        for entry in fractions:
            denominator = entry.denominator
            multiplier = multiplier * denominator // _gcd(multiplier, denominator)
        cleared.append([int(entry * multiplier) for entry in fractions])
    if not cleared:
        return 0

    height, width = len(cleared), len(cleared[0])
    previous_pivot = 1
    rank = 0
    for column in range(width):
        pivot = None
        for index in range(rank, height):
            if cleared[index][column] != 0:
                pivot = index
                break
        if pivot is None:
            continue
        cleared[rank], cleared[pivot] = cleared[pivot], cleared[rank]
        pivot_value = cleared[rank][column]
        for index in range(rank + 1, height):
            factor = cleared[index][column]
            for j in range(width):
                numerator = pivot_value * cleared[index][j] - factor * cleared[rank][j]
                quotient, remainder = divmod(numerator, previous_pivot)
                if remainder:
                    raise AssertionError("Bareiss elimination left the integers")
                cleared[index][j] = quotient
        previous_pivot = pivot_value
        rank += 1
        if rank == height:
            break
    return rank


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return abs(a)


def matmul(left: Matrix, right: Matrix) -> Matrix:
    inner = len(right)
    width = len(right[0])
    return [
        [sum((row[k] * right[k][j] for k in range(inner)), Fraction(0)) for j in range(width)]
        for row in left
    ]


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(x, y)] for x, y in zip(left, right)]


def subtract(left: Matrix, right: Matrix) -> Matrix:
    return [[a - b for a, b in zip(x, y)] for x, y in zip(left, right)]


def is_zero(matrix: Matrix) -> bool:
    return all(entry == 0 for row in matrix for entry in row)


def is_symmetric(matrix: Matrix) -> bool:
    return is_zero(subtract(matrix, transpose(matrix)))


def identity(size: int) -> Matrix:
    return [[Fraction(1 if i == j else 0) for j in range(size)] for i in range(size)]


def determinant(matrix: Matrix) -> Fraction:
    """Exact determinant by Gaussian elimination over Q."""
    work = [list(row) for row in matrix]
    size = len(work)
    result = Fraction(1)
    for column in range(size):
        pivot = None
        for index in range(column, size):
            if work[index][column] != 0:
                pivot = index
                break
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        result *= work[column][column]
        inverse = Fraction(1) / work[column][column]
        work[column] = [entry * inverse for entry in work[column]]
        for index in range(column + 1, size):
            factor = work[index][column]
            if factor != 0:
                work[index] = [a - factor * b for a, b in zip(work[index], work[column])]
    return result


def render(matrix: Matrix) -> list[list[str]]:
    """Canonical string rendering so certificates stay byte-deterministic."""
    return [[str(entry) for entry in row] for row in matrix]
