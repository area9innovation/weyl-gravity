"""Exact projector onto the fifteen conformal-Killing reducibilities.

The flat polynomial realization is globally related to the conformal cylinder
by radial compactification.  It is especially convenient for a finite exact
projector: conformal Killing parameters have vector degree at most two and
Weyl-scalar degree at most one.  The ordered basis is

``4 translations | 6 rotations + dilation | 4 special conformal``

and hence realizes the compact ``4_-1 + 7_0 + 4_+1`` decomposition after the
standard cylinder change of basis.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product

import sympy as sp


DIMENSION = 4
SYMMETRIC_PAIRS = tuple(
    (first, second)
    for first in range(DIMENSION)
    for second in range(first, DIMENSION)
)


def homogeneous_monomials(degree: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        exponent
        for exponent in product(range(degree + 1), repeat=DIMENSION)
        if sum(exponent) == degree
    )


def _differentiate(exponent: tuple[int, ...], axis: int):
    if exponent[axis] == 0:
        return None
    output = list(exponent)
    coefficient = output[axis]
    output[axis] -= 1
    return sp.Integer(coefficient), tuple(output)


@dataclass(frozen=True)
class CKVProjector:
    gauge_map: sp.SparseMatrix
    basis: sp.Matrix
    left_inverse: sp.Matrix
    projector: sp.Matrix
    compact_degrees: tuple[int, ...]
    labels: tuple[str, ...]

    def verify(self) -> None:
        identity = sp.eye(self.basis.cols)
        if self.basis.shape != (65, 15):
            raise AssertionError("unexpected CKV basis shape")
        if self.gauge_map.shape != (50, 65):
            raise AssertionError("unexpected low-mode gauge-map shape")
        if self.left_inverse * self.basis != identity:
            raise AssertionError("CKV left inverse failed")
        if self.projector != self.basis * self.left_inverse:
            raise AssertionError("projector factorization failed")
        if self.projector * self.projector != self.projector:
            raise AssertionError("P_CKV is not idempotent")
        if self.gauge_map * self.projector != sp.zeros(50, 65):
            raise AssertionError("K P_CKV != 0")
        if self.gauge_map * self.basis != sp.zeros(50, 15):
            raise AssertionError("explicit CKVs are not in ker K")
        if self.gauge_map.rank() != 50:
            raise AssertionError("low-mode K does not have nullity fifteen")
        if self.basis.rank() != 15:
            raise AssertionError("CKV basis is dependent")
        if self.compact_degrees != (-1,) * 4 + (0,) * 7 + (1,) * 4:
            raise AssertionError("wrong 4+7+4 grading")


def _low_mode_gauge_map():
    vector_exponents = tuple(
        exponent
        for degree in range(3)
        for exponent in homogeneous_monomials(degree)
    )
    scalar_exponents = tuple(
        exponent
        for degree in range(2)
        for exponent in homogeneous_monomials(degree)
    )
    metric_exponents = tuple(
        exponent
        for degree in range(2)
        for exponent in homogeneous_monomials(degree)
    )
    vector_columns = {
        (component, exponent): column
        for column, (component, exponent) in enumerate(
            product(range(DIMENSION), vector_exponents)
        )
    }
    scalar_offset = len(vector_columns)
    scalar_columns = {
        exponent: scalar_offset + column
        for column, exponent in enumerate(scalar_exponents)
    }
    rows = {
        (pair, exponent): row
        for row, (pair, exponent) in enumerate(
            product(SYMMETRIC_PAIRS, metric_exponents)
        )
    }
    entries: defaultdict[tuple[int, int], sp.Expr] = defaultdict(
        lambda: sp.Integer(0)
    )
    for (component, exponent), column in vector_columns.items():
        for first, second in SYMMETRIC_PAIRS:
            for derivative, target in ((first, second), (second, first)):
                if component != target:
                    continue
                result = _differentiate(exponent, derivative)
                if result is not None:
                    coefficient, output = result
                    entries[rows[((first, second), output)], column] += coefficient
    for exponent, column in scalar_columns.items():
        for index in range(DIMENSION):
            entries[rows[((index, index), exponent)], column] += 2
    return (
        sp.SparseMatrix(len(rows), len(vector_columns) + len(scalar_columns), entries),
        vector_columns,
        scalar_columns,
    )


def _parameter_vector(vector_columns, scalar_columns, vectors, scalars):
    output = sp.zeros(len(vector_columns) + len(scalar_columns), 1)
    for key, value in vectors.items():
        output[vector_columns[key]] += value
    for key, value in scalars.items():
        output[scalar_columns[key]] += value
    return output


def _ckv_basis(vector_columns, scalar_columns):
    zero = (0, 0, 0, 0)
    unit = tuple(
        tuple(1 if coordinate == axis else 0 for coordinate in range(DIMENSION))
        for axis in range(DIMENSION)
    )
    vectors: list[sp.Matrix] = []
    labels: list[str] = []

    for component in range(DIMENSION):
        vectors.append(
            _parameter_vector(
                vector_columns,
                scalar_columns,
                {(component, zero): 1},
                {},
            )
        )
        labels.append(f"P{component}")

    for first in range(DIMENSION):
        for second in range(first + 1, DIMENSION):
            vectors.append(
                _parameter_vector(
                    vector_columns,
                    scalar_columns,
                    {
                        (first, unit[second]): 1,
                        (second, unit[first]): -1,
                    },
                    {},
                )
            )
            labels.append(f"M{first}{second}")
    vectors.append(
        _parameter_vector(
            vector_columns,
            scalar_columns,
            {(axis, unit[axis]): 1 for axis in range(DIMENSION)},
            {zero: -1},
        )
    )
    labels.append("D")

    for direction in range(DIMENSION):
        vector_terms: defaultdict[tuple[int, tuple[int, ...]], sp.Expr] = defaultdict(
            lambda: sp.Integer(0)
        )
        for component in range(DIMENSION):
            exponent = list(unit[direction])
            exponent[component] += 1
            vector_terms[component, tuple(exponent)] += 2
        for axis in range(DIMENSION):
            exponent = [0] * DIMENSION
            exponent[axis] = 2
            vector_terms[direction, tuple(exponent)] -= 1
        vectors.append(
            _parameter_vector(
                vector_columns,
                scalar_columns,
                dict(vector_terms),
                {unit[direction]: -2},
            )
        )
        labels.append(f"K{direction}")
    return sp.Matrix.hstack(*vectors), tuple(labels)


def conformal_killing_projector() -> CKVProjector:
    gauge, vector_columns, scalar_columns = _low_mode_gauge_map()
    basis, labels = _ckv_basis(vector_columns, scalar_columns)

    # Pivot columns of basis.T are independent rows of basis.  Selecting them
    # gives an exact 15x15 coordinate chart and hence a rational left inverse.
    _, pivot_rows = basis.T.rref()
    if len(pivot_rows) != 15:
        raise AssertionError("could not find fifteen independent CKV rows")
    selection = sp.zeros(15, basis.rows)
    for row, source_row in enumerate(pivot_rows):
        selection[row, source_row] = 1
    left_inverse = (selection * basis).inv() * selection
    projector = sp.simplify(basis * left_inverse)
    result = CKVProjector(
        gauge,
        basis,
        left_inverse,
        projector,
        (-1,) * 4 + (0,) * 7 + (1,) * 4,
        labels,
    )
    result.verify()
    return result
