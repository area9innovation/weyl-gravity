"""Component-aware composition of parallel operators on the 24-field bundle.

The derivative normal-form engine acts on abstract covariant tensor slots.
This adapter converts the ``h[10]+f[10]+v[4]`` component convention to those
slots, composes sparse parallel coefficient tables, and converts curvature-
changed slots back to component columns.  It is the required backend for the
quadratic lower-order factor solve; ordinary Fourier-polynomial matrix
multiplication is insufficient at orders two and zero.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping

import sympy as sp

from .conventions import SYMMETRIC_COORDINATES, _ordinary_system
from .derivative_normal_form import ParallelCylinderNormalForm


OperatorTable = Mapping[tuple[int, ...], sp.Matrix]


def _column_slots(column: int) -> tuple[int, tuple[int, ...]]:
    if column < 10:
        return 0, SYMMETRIC_COORDINATES[column]
    if column < 20:
        return 10, SYMMETRIC_COORDINATES[column - 10]
    if column < 24:
        return 20, (column - 20,)
    raise IndexError(column)


def _slots_column(block: int, slots: tuple[int, ...]) -> int:
    if block in (0, 10):
        return block + SYMMETRIC_COORDINATES.index(tuple(sorted(slots)))
    if block == 20:
        return 20 + slots[0]
    raise ValueError(block)


def polynomial_table(
    matrix: sp.Matrix,
    covector: tuple[sp.Symbol, ...],
    maximum_order: int,
) -> dict[tuple[int, ...], sp.Matrix]:
    """Convert a canonical covector polynomial to derivative-word tables."""

    output: dict[tuple[int, ...], sp.Matrix] = {}
    for degree in range(maximum_order + 1):
        for multiindex in __import__("itertools").product(
            range(degree + 1), repeat=4
        ):
            if sum(multiindex) != degree:
                continue
            word = tuple(
                axis for axis, count in enumerate(multiindex) for _ in range(count)
            )
            coefficient = matrix.applyfunc(
                lambda entry: sp.Poly(entry, *covector).coeff_monomial(
                    sp.prod(covector[a] ** multiindex[a] for a in range(4))
                )
            )
            if coefficient != sp.zeros(24):
                output[word] = coefficient
    return output


@dataclass(frozen=True)
class ParallelFieldOperatorComposer:
    normal_form: ParallelCylinderNormalForm

    @staticmethod
    def build() -> "ParallelFieldOperatorComposer":
        result = ParallelFieldOperatorComposer(ParallelCylinderNormalForm.build())
        result.verify()
        return result

    def compose(
        self, outer: OperatorTable, inner: OperatorTable
    ) -> dict[tuple[int, ...], sp.Matrix]:
        result: dict[tuple[int, ...], sp.Matrix] = defaultdict(lambda: sp.zeros(24))
        for outer_word, outer_matrix in outer.items():
            outer_nonzero = [
                (row, middle, outer_matrix[row, middle])
                for row in range(24)
                for middle in range(24)
                if outer_matrix[row, middle] != 0
            ]
            for inner_word, inner_matrix in inner.items():
                inner_by_row = {
                    middle: [
                        (column, inner_matrix[middle, column])
                        for column in range(24)
                        if inner_matrix[middle, column] != 0
                    ]
                    for middle in range(24)
                }
                for row, middle, left in outer_nonzero:
                    for column, right in inner_by_row[middle]:
                        block, slots = _column_slots(column)
                        canonical = self.normal_form.canonicalize(
                            {(outer_word + inner_word, slots): left * right}
                        )
                        for (word, changed_slots), coefficient in canonical.items():
                            changed_column = _slots_column(block, changed_slots)
                            result[word][row, changed_column] += coefficient
        return {
            word: matrix.applyfunc(sp.expand)
            for word, matrix in result.items()
            if matrix != sp.zeros(24)
        }

    def verify(self) -> None:
        identity = {(): sp.eye(24)}
        if self.compose(identity, identity) != identity:
            raise AssertionError("parallel operator identity composition failed")
        metric = _ordinary_system().metric
        box = {
            (axis, axis): metric[axis, axis] * sp.eye(24)
            for axis in range(4)
        }
        box_square = self.compose(box, box)
        if max(map(len, box_square)) != 4:
            raise AssertionError("box-square principal order drifted")
        if not any(len(word) == 2 for word in box_square):
            raise AssertionError("tensor curvature terms in box-square were omitted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        metric = _ordinary_system().metric
        box = {
            (axis, axis): metric[axis, axis] * sp.eye(24)
            for axis in range(4)
        }
        square = self.compose(box, box)
        return {
            "schema": "pure-weyl-parallel-24-field-operator-composer-v1",
            "bundle_order": "h[10]+f[10]+v[4]",
            "canonical_derivative_order": "nondecreasing indices",
            "curvature_action_slots": "inner derivatives plus every input tensor slot",
            "parallel_coefficient_assumption": True,
            "identity_composition": True,
            "box_square_orders": sorted({len(word) for word in square}),
            "box_square_order_two_curvature_present": True,
            "quadratic_factor_rank_solve_completed": False,
            "scope": (
                "exact composition backend is now available; applying it to the "
                "45-parameter nonlinear quadratic factor family is the next solve"
            ),
        }
