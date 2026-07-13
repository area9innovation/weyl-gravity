#!/usr/bin/env python3
"""Exact finite-dimensional BRST pairing-descent certificate.

This is a linear-algebra certificate, not a construction of the pure-Weyl
global BRST complex.  It records the conditions that a future oscillator plus
ghost realization must satisfy before its indefinite form can be quoted on
BRST cohomology.

For a nondegenerate Hermitian form ``G`` and nilpotent state-space BRST matrix
``Q``, the relevant adjoint is

    Q^sharp = G^{-1} Q^dagger G.

The standard BRST convention is ``Q^sharp=Q`` (an overall ``-`` is equivalent
after replacing a Hermitian BRST charge by an anti-Hermitian differential).
Then

    im Q = (ker Q)^perp,

so the radical of ``G`` restricted to ``ker Q`` is exactly ``im Q`` and the
quotient ``ker Q / im Q`` inherits a nondegenerate Hermitian form.

The executable also implements the more general, degreewise test.  Given

    C^(n-1) --d_prev--> C^n --d_next--> C^(n+1),

the form ``G_n`` descends to ``H^n`` if and only if

    (im d_prev)^dagger G_n (ker d_next) = 0.

Nilpotency alone does not imply this condition.  If the restricted radical is
larger than the exact subspace, the quotient form exists but remains
degenerate.  The exact routines below construct a quotient complement, its
Gram matrix, its radical, and its inertia without floating-point arithmetic.
"""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp


def check(label: str, condition: object) -> None:
    if not bool(condition):
        raise AssertionError(label)
    print("[OK ] " + label)


def dagger(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.conjugate().T


def exact_zero(matrix: sp.Matrix) -> bool:
    return all(sp.simplify(entry) == 0 for entry in matrix)


def columns(vectors: list[sp.Matrix], rows: int) -> sp.Matrix:
    return sp.Matrix.hstack(*vectors) if vectors else sp.zeros(rows, 0)


def column_basis(matrix: sp.Matrix) -> sp.Matrix:
    return columns(matrix.columnspace(), matrix.rows)


def null_basis(matrix: sp.Matrix) -> sp.Matrix:
    return columns(matrix.nullspace(), matrix.cols)


def same_span(first: sp.Matrix, second: sp.Matrix) -> bool:
    if first.rows != second.rows:
        return False
    rank_first = first.rank()
    rank_second = second.rank()
    return (
        rank_first == rank_second
        and sp.Matrix.hstack(first, second).rank() == rank_first
    )


def coordinates_in_basis(basis: sp.Matrix, vectors: sp.Matrix) -> sp.Matrix:
    """Coordinates of columns of ``vectors`` in the full-column-rank basis."""

    if vectors.cols == 0:
        return sp.zeros(basis.cols, 0)
    solutions = []
    for vector in vectors.columnspace():
        solution, parameters = basis.gauss_jordan_solve(vector)
        if parameters.rows:
            # ``basis`` is a basis, so an in-span vector has a unique solution.
            raise AssertionError("coordinate solution unexpectedly non-unique")
        solutions.append(solution)
    return columns(solutions, basis.cols)


def quotient_complement(exact_coordinates: sp.Matrix, closed_dimension: int) -> sp.Matrix:
    """Extend exact coordinates to a basis and return the added columns."""

    current = exact_coordinates.columnspace()
    current_matrix = columns(current, closed_dimension)
    current_rank = current_matrix.rank()
    complement: list[sp.Matrix] = []
    for index in range(closed_dimension):
        candidate = sp.eye(closed_dimension)[:, index]
        trial = sp.Matrix.hstack(current_matrix, candidate)
        if trial.rank() > current_rank:
            complement.append(candidate)
            current_matrix = trial
            current_rank += 1
        if current_rank == closed_dimension:
            break
    if current_rank != closed_dimension:
        raise AssertionError("failed to extend exact coordinates to a basis")
    return columns(complement, closed_dimension)


def exact_real_sign(value: sp.Expr) -> int:
    value = sp.simplify(value)
    if sp.simplify(value - sp.conjugate(value)) != 0:
        raise ValueError(f"Hermitian pivot is not provably real: {value}")
    if value.is_positive:
        return 1
    if value.is_negative:
        return -1
    if value == 0:
        return 0
    raise ValueError(f"sign is not decidable exactly: {value}")


def exact_hermitian_inertia(matrix: sp.Matrix) -> tuple[int, int, int]:
    """Return ``(positive, negative, zero)`` by exact Hermitian congruence.

    One-by-one pivots use exact real signs.  If every diagonal entry vanishes
    but an off-diagonal entry remains, its nonsingular 2-by-2 Hermitian block
    contributes one positive and one negative direction.  Schur complements
    implement congruences, so Sylvester inertia is preserved.
    """

    work = matrix.applyfunc(sp.simplify)
    if work.rows != work.cols or not exact_zero(work - dagger(work)):
        raise ValueError("inertia requires a square Hermitian matrix")

    positive = negative = zero = 0
    while work.rows:
        dimension = work.rows
        diagonal = next(
            (index for index in range(dimension) if work[index, index] != 0),
            None,
        )
        if diagonal is not None:
            order = [diagonal] + [i for i in range(dimension) if i != diagonal]
            work = work.extract(order, order)
            pivot = sp.simplify(work[0, 0])
            sign = exact_real_sign(pivot)
            positive += int(sign > 0)
            negative += int(sign < 0)
            if dimension == 1:
                break
            row = work[:1, 1:]
            column = work[1:, :1]
            work = (work[1:, 1:] - column * row / pivot).applyfunc(sp.simplify)
            continue

        off_diagonal = next(
            (
                (row, column)
                for row in range(dimension)
                for column in range(row + 1, dimension)
                if work[row, column] != 0
            ),
            None,
        )
        if off_diagonal is None:
            zero += dimension
            break

        first, second = off_diagonal
        order = [first, second] + [
            i for i in range(dimension) if i not in (first, second)
        ]
        work = work.extract(order, order)
        pivot = work[:2, :2]
        off_diagonal_norm = sp.simplify(
            sp.conjugate(pivot[0, 1]) * pivot[0, 1]
        )
        if sp.simplify(pivot.det() + off_diagonal_norm) != 0:
            raise AssertionError(
                "zero-diagonal Hermitian pivot does not have opposite signs"
            )
        positive += 1
        negative += 1
        if dimension == 2:
            break
        work = (
            work[2:, 2:]
            - work[2:, :2] * pivot.inv() * work[:2, 2:]
        ).applyfunc(sp.simplify)

    return positive, negative, zero


@dataclass(frozen=True)
class CohomologyPairing:
    closed: sp.Matrix
    exact: sp.Matrix
    restricted_gram: sp.Matrix
    exact_coordinates: sp.Matrix
    radical_coordinates: sp.Matrix
    representatives: sp.Matrix
    quotient_gram: sp.Matrix
    inertia: tuple[int, int, int]


def degreewise_pairing(
    differential_previous: sp.Matrix,
    differential_next: sp.Matrix,
    gram: sp.Matrix,
) -> CohomologyPairing:
    """Construct the exact degreewise cohomology pairing data."""

    if differential_previous.rows != gram.rows:
        raise ValueError("previous differential must land in the Gram space")
    if differential_next.cols != gram.cols:
        raise ValueError("next differential must leave the Gram space")
    if gram.rows != gram.cols or not exact_zero(gram - dagger(gram)):
        raise ValueError("degreewise Gram matrix must be Hermitian")
    if not exact_zero(differential_next * differential_previous):
        raise ValueError("the supplied maps do not form a complex")

    closed = null_basis(differential_next)
    exact = column_basis(differential_previous)
    if sp.Matrix.hstack(closed, exact).rank() != closed.rank():
        raise AssertionError("exact vectors are not closed")

    descent = dagger(exact) * gram * closed
    if not exact_zero(descent):
        raise ValueError("the form does not descend: exacts pair with closed states")

    restricted = (dagger(closed) * gram * closed).applyfunc(sp.simplify)
    exact_coordinates = coordinates_in_basis(closed, exact)
    radical_coordinates = null_basis(restricted)
    complement = quotient_complement(exact_coordinates, closed.cols)
    representatives = closed * complement
    quotient = (dagger(representatives) * gram * representatives).applyfunc(
        sp.simplify
    )
    return CohomologyPairing(
        closed=closed,
        exact=exact,
        restricted_gram=restricted,
        exact_coordinates=exact_coordinates,
        radical_coordinates=radical_coordinates,
        representatives=representatives,
        quotient_gram=quotient,
        inertia=exact_hermitian_inertia(quotient),
    )


# ---------------------------------------------------------------------------
# A complete ghost-number-reflected BRST quartet plus two physical states.
# ---------------------------------------------------------------------------
# Basis: (a_-1, b_0, c_0, d_+1, p_0, n_0).
# Q a=b, Q c=d.  G pairs a with d and b with c; p and n survive with
# positive and negative norms.  Here the centered ghost-number metric pairs
# degree r with degree -r (the general relation is r with nu-r), which is why
# a degree-raising Q can be G-self-adjoint.
Q = sp.zeros(6)
Q[1, 0] = 1
Q[3, 2] = 1

G = sp.zeros(6)
G[0, 3] = G[3, 0] = 1
G[1, 2] = G[2, 1] = 1
G[4, 4] = 1
G[5, 5] = -1

ghost_number = sp.diag(-1, 0, 0, 1, 0, 0)

check("C2g-P: fixture BRST matrix is nilpotent", Q**2 == sp.zeros(6))
check("C2g-P: total indefinite form is nondegenerate Hermitian", G.det() != 0 and G == dagger(G))
check("C2g-P: BRST charge is G-self-adjoint", dagger(Q) * G == G * Q)
check("C2g-P: Q raises ghost number by one", ghost_number * Q - Q * ghost_number == Q)
check(
    "C2g-P: ghost number is G-skew under the degree-reflecting pairing",
    G.inv() * dagger(ghost_number) * G == -ghost_number,
)

# For the total complex ``ker Q / im Q``, pass Q as both the incoming image
# and outgoing differential.  Construct the data directly because the
# degreewise helper represents one fixed ghost-number sector, whereas this
# first check uses the whole degree-reflected complex.
closed_total = null_basis(Q)
exact_total = column_basis(Q)
restricted_total = dagger(closed_total) * G * closed_total
exact_coordinates_total = coordinates_in_basis(closed_total, exact_total)
radical_total = null_basis(restricted_total)
complement_total = quotient_complement(exact_coordinates_total, closed_total.cols)
representatives_total = closed_total * complement_total
quotient_total = dagger(representatives_total) * G * representatives_total

check(
    "C2g-P: every exact state is null against every closed state",
    exact_zero(dagger(exact_total) * G * closed_total),
)
check(
    "C2g-P: restricted radical equals the exact subspace",
    same_span(exact_coordinates_total, radical_total),
)
check(
    "C2g-P: cohomology Gram is nondegenerate with signature (1,1)",
    quotient_total.det() != 0
    and exact_hermitian_inertia(quotient_total) == (1, 1, 0),
)

# Representative independence: adding arbitrary exact columns cannot change
# the quotient Gram because exacts lie in the radical of the closed form.
shift = sp.Matrix([[2, -3], [5, 7]])
shifted_representatives = representatives_total + exact_total * shift
check(
    "C2g-P: quotient Gram is independent of exact representative shifts",
    dagger(shifted_representatives) * G * shifted_representatives
    == quotient_total,
)


# ---------------------------------------------------------------------------
# The middle-degree algorithm and its adjoint relation.
# ---------------------------------------------------------------------------
G_zero = sp.Matrix(
    [
        [0, 1, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, -1],
    ]
)
d_previous = sp.Matrix([1, 0, 0, 0])
d_next = sp.Matrix([[0, 1, 0, 0]])
check("C2g-P: degreewise fixture is a complex", d_next * d_previous == sp.zeros(1))
check(
    "C2g-P: incoming and outgoing maps obey the reflected adjoint relation",
    d_next == dagger(d_previous) * G_zero,
)
middle = degreewise_pairing(d_previous, d_next, G_zero)
check(
    "C2g-P: degree-zero radical is exactly the incoming exact line",
    same_span(middle.exact_coordinates, middle.radical_coordinates),
)
check(
    "C2g-P: exact quotient algorithm returns the physical (1,1) signature",
    middle.inertia == (1, 1, 0),
)


# ---------------------------------------------------------------------------
# Descent can hold while the quotient form remains degenerate.
# ---------------------------------------------------------------------------
G_extra_radical = sp.Matrix(
    [
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [1, 0, 0, 0],
        [0, 1, 0, 0],
    ]
)
d_previous_extra = sp.Matrix([1, 0, 0, 0])
d_next_extra = sp.Matrix([[0, 0, 1, 0], [0, 0, 0, 1]])
extra_radical = degreewise_pairing(
    d_previous_extra, d_next_extra, G_extra_radical
)
check(
    "C2g-P: descent alone need not identify the whole closed-state radical",
    not same_span(
        extra_radical.exact_coordinates, extra_radical.radical_coordinates
    ),
)
check(
    "C2g-P: an unremoved radical is reported as a zero cohomology direction",
    extra_radical.inertia == (0, 0, 1),
)


# ---------------------------------------------------------------------------
# Nilpotency without the adjoint condition is insufficient.
# ---------------------------------------------------------------------------
Q_bad = sp.Matrix([[0, 1], [0, 0]])
G_bad = sp.eye(2)
closed_bad = null_basis(Q_bad)
exact_bad = column_basis(Q_bad)
check("C2g-P: counterexample differential is nilpotent", Q_bad**2 == sp.zeros(2))
check(
    "C2g-P: nilpotency alone does not make exacts null against closed states",
    not exact_zero(dagger(exact_bad) * G_bad * closed_bad),
)
check(
    "C2g-P: the failed descent is detected by failed G-adjointness",
    dagger(Q_bad) * G_bad != G_bad * Q_bad,
)


print("total cohomology Gram:", quotient_total)
print("total cohomology inertia (+,-,0):", exact_hermitian_inertia(quotient_total))
print("middle-degree cohomology Gram:", middle.quotient_gram)
print("CONFORMAL C2g-P BRST PAIRING DESCENT: ALL PASS")
