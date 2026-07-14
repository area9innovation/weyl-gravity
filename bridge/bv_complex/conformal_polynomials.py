"""Generalized-Verma polynomial modules for the four-dimensional conformal algebra.

States at descendant level ``k`` are homogeneous polynomials in four
commuting translation generators ``P_mu`` tensored with a finite ``SO(4)``
spin space.  In this realization

``D = Delta + N``

and

``K_mu = 2(Delta+N) d_mu - P_mu d^2 - 2 S_{mu nu} d_nu``.

The formula obeys ``[K_mu,P_nu]=2 delta_mu_nu D-2 M_mu_nu`` with
``M_mu_nu=S_mu_nu+P_mu d_nu-P_nu d_mu``.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product

import sympy as sp


DIMENSION = 4
SYMMETRIC_PAIRS = tuple(
    (first, second)
    for first in range(DIMENSION)
    for second in range(first, DIMENSION)
)


def homogeneous_monomials(level: int) -> tuple[tuple[int, ...], ...]:
    if level < 0:
        return ()
    return tuple(
        exponent
        for exponent in product(range(level + 1), repeat=DIMENSION)
        if sum(exponent) == level
    )


def scalar_spin() -> tuple[sp.SparseMatrix, ...]:
    return tuple(sp.SparseMatrix(1, 1, {}) for _ in range(6))


ROTATION_PAIRS = tuple(
    (first, second)
    for first in range(DIMENSION)
    for second in range(first + 1, DIMENSION)
)


def vector_spin() -> tuple[sp.SparseMatrix, ...]:
    output = []
    for first, second in ROTATION_PAIRS:
        matrix = sp.MutableSparseMatrix(DIMENSION, DIMENSION, {})
        # S_ab e_r = delta_br e_a-delta_ar e_b.
        matrix[first, second] = 1
        matrix[second, first] = -1
        output.append(sp.SparseMatrix(matrix))
    return tuple(output)


def symmetric_spin() -> tuple[sp.SparseMatrix, ...]:
    vector = vector_spin()
    output = []
    for spin in vector:
        matrix = sp.MutableSparseMatrix(len(SYMMETRIC_PAIRS), len(SYMMETRIC_PAIRS), {})
        for column, (left, right) in enumerate(SYMMETRIC_PAIRS):
            tensor = sp.zeros(DIMENSION)
            tensor[left, right] = tensor[right, left] = 1
            transformed = spin * tensor + tensor * spin.T
            for row, (target_left, target_right) in enumerate(SYMMETRIC_PAIRS):
                matrix[row, column] = transformed[target_left, target_right]
        output.append(sp.SparseMatrix(matrix))
    return tuple(output)


def tracefree_component_maps() -> tuple[sp.SparseMatrix, sp.SparseMatrix]:
    """Inclusion/projection for a concrete nine-component trace-free basis."""

    pair_index = {pair: index for index, pair in enumerate(SYMMETRIC_PAIRS)}
    columns = []
    for pair in SYMMETRIC_PAIRS:
        if pair[0] != pair[1]:
            vector = sp.zeros(10, 1)
            vector[pair_index[pair]] = 1
            columns.append(vector)
    for diagonal in range(3):
        vector = sp.zeros(10, 1)
        vector[pair_index[(diagonal, diagonal)]] = 1
        vector[pair_index[(3, 3)]] = -1
        columns.append(vector)
    inclusion = sp.SparseMatrix(sp.Matrix.hstack(*columns))
    projection = sp.SparseMatrix(
        (inclusion.T * inclusion).inv() * inclusion.T
    )
    if projection * inclusion != sp.eye(9):
        raise AssertionError("trace-free component splitting failed")
    return inclusion, projection


TRACEFREE_INCLUSION, TRACEFREE_PROJECTION = tracefree_component_maps()


def tracefree_symmetric_spin() -> tuple[sp.SparseMatrix, ...]:
    output = tuple(
        sp.SparseMatrix(TRACEFREE_PROJECTION * matrix * TRACEFREE_INCLUSION)
        for matrix in symmetric_spin()
    )
    return output


SPIN_REPRESENTATIONS = {
    "scalar": (1, scalar_spin()),
    "vector": (4, vector_spin()),
    "symmetric": (10, symmetric_spin()),
    "symmetric_tf": (9, tracefree_symmetric_spin()),
}


def _derivative(exponent: tuple[int, ...], axis: int):
    if exponent[axis] == 0:
        return None
    output = list(exponent)
    coefficient = output[axis]
    output[axis] -= 1
    return sp.Integer(coefficient), tuple(output)


@dataclass(frozen=True)
class PolynomialConformalModule:
    dimension_primary: sp.Expr
    spin_kind: str

    @property
    def spin_dimension(self) -> int:
        return SPIN_REPRESENTATIONS[self.spin_kind][0]

    @property
    def spin(self) -> tuple[sp.SparseMatrix, ...]:
        return SPIN_REPRESENTATIONS[self.spin_kind][1]

    def basis(self, level: int) -> tuple[tuple[int, tuple[int, ...]], ...]:
        return tuple(product(range(self.spin_dimension), homogeneous_monomials(level)))

    def dimension(self, level: int) -> int:
        return len(self.basis(level))

    def dilation(self, level: int) -> sp.SparseMatrix:
        return (self.dimension_primary + level) * sp.SparseMatrix.eye(self.dimension(level))

    def translation(self, axis: int, level: int) -> sp.SparseMatrix:
        """Descendant-basis translation (multiplication by ``P_axis``)."""
        source = self.basis(level)
        target = self.basis(level + 1)
        target_index = {value: index for index, value in enumerate(target)}
        entries = {}
        for column, (spin, exponent) in enumerate(source):
            output = list(exponent)
            output[axis] += 1
            entries[target_index[(spin, tuple(output))], column] = 1
        return sp.SparseMatrix(len(target), len(source), entries)

    def coordinate_translation(self, axis: int, level: int) -> sp.SparseMatrix:
        """Coordinate-field translation ``partial_axis`` (level ``k->k-1``)."""

        source = self.basis(level)
        target = self.basis(level - 1)
        target_index = {value: index for index, value in enumerate(target)}
        entries = {}
        for column, (spin, exponent) in enumerate(source):
            derivative = _derivative(exponent, axis)
            if derivative is not None:
                coefficient, output = derivative
                entries[target_index[(spin, output)], column] = coefficient
        return sp.SparseMatrix(len(target), len(source), entries)

    def rotation(self, first: int, second: int, level: int) -> sp.SparseMatrix:
        if first >= second:
            raise ValueError("rotation pair must be ordered")
        source = self.basis(level)
        index = {value: position for position, value in enumerate(source)}
        spin = self.spin[ROTATION_PAIRS.index((first, second))]
        entries: dict[tuple[int, int], sp.Expr] = {}
        for column, (spin_component, exponent) in enumerate(source):
            for target_spin in range(self.spin_dimension):
                value = spin[target_spin, spin_component]
                if value:
                    entries[index[(target_spin, exponent)], column] = value
            # P_first d_second-P_second d_first.
            for sign, multiply_axis, derivative_axis in (
                (1, first, second),
                (-1, second, first),
            ):
                derivative = _derivative(exponent, derivative_axis)
                if derivative is None:
                    continue
                coefficient, output = derivative
                output = list(output)
                output[multiply_axis] += 1
                row = index[(spin_component, tuple(output))]
                entries[row, column] = entries.get((row, column), 0) + sign * coefficient
        return sp.SparseMatrix(len(source), len(source), entries)

    def special_conformal(self, axis: int, level: int) -> sp.SparseMatrix:
        """Map descendant level ``level`` to ``level-1``."""

        source = self.basis(level)
        target = self.basis(level - 1)
        if not target:
            return sp.SparseMatrix(0, len(source), {})
        target_index = {value: index for index, value in enumerate(target)}
        entries: dict[tuple[int, int], sp.Expr] = {}
        for column, (spin_component, exponent) in enumerate(source):
            # 2(Delta+N) d_axis; N acts after the derivative.
            derivative = _derivative(exponent, axis)
            if derivative is not None:
                coefficient, output = derivative
                row = target_index[(spin_component, output)]
                entries[row, column] = entries.get((row, column), 0) + 2 * (
                    self.dimension_primary + level - 1
                ) * coefficient

            # -P_axis d^2.
            for contracted in range(DIMENSION):
                first = _derivative(exponent, contracted)
                if first is None:
                    continue
                first_coefficient, first_output = first
                second = _derivative(first_output, contracted)
                if second is None:
                    continue
                second_coefficient, output = second
                output = list(output)
                output[axis] += 1
                row = target_index[(spin_component, tuple(output))]
                entries[row, column] = entries.get((row, column), 0) - first_coefficient * second_coefficient

            # -2 S_axis,nu d_nu.
            for contracted in range(DIMENSION):
                if contracted == axis:
                    continue
                ordered = tuple(sorted((axis, contracted)))
                spin_matrix = self.spin[ROTATION_PAIRS.index(ordered)]
                orientation = 1 if axis < contracted else -1
                derivative = _derivative(exponent, contracted)
                if derivative is None:
                    continue
                coefficient, output = derivative
                for target_spin in range(self.spin_dimension):
                    spin_value = orientation * spin_matrix[target_spin, spin_component]
                    if spin_value:
                        row = target_index[(target_spin, output)]
                        entries[row, column] = entries.get((row, column), 0) - 2 * coefficient * spin_value
        return sp.SparseMatrix(len(target), len(source), entries)

    def coordinate_special(self, axis: int, level: int) -> sp.SparseMatrix:
        """Coordinate-field special conformal action (level ``k->k+1``).

        The convention is

        ``K_mu=2 x_mu(Delta+x.d)-x^2 d_mu+2 x^nu S_mu,nu``.
        """

        source = self.basis(level)
        target = self.basis(level + 1)
        target_index = {value: index for index, value in enumerate(target)}
        entries: dict[tuple[int, int], sp.Expr] = {}
        for column, (spin_component, exponent) in enumerate(source):
            # 2 x_axis (Delta+N).
            output = list(exponent)
            output[axis] += 1
            row = target_index[(spin_component, tuple(output))]
            entries[row, column] = entries.get((row, column), 0) + 2 * (
                self.dimension_primary + level
            )

            # -x^2 d_axis.
            derivative = _derivative(exponent, axis)
            if derivative is not None:
                coefficient, reduced = derivative
                for contracted in range(DIMENSION):
                    output = list(reduced)
                    output[contracted] += 2
                    row = target_index[(spin_component, tuple(output))]
                    entries[row, column] = entries.get((row, column), 0) - coefficient

            # +2 x^nu S_axis,nu.
            for contracted in range(DIMENSION):
                if contracted == axis:
                    continue
                ordered = tuple(sorted((axis, contracted)))
                spin_matrix = self.spin[ROTATION_PAIRS.index(ordered)]
                orientation = 1 if axis < contracted else -1
                output = list(exponent)
                output[contracted] += 1
                for target_spin in range(self.spin_dimension):
                    value = orientation * spin_matrix[target_spin, spin_component]
                    if value:
                        row = target_index[(target_spin, tuple(output))]
                        entries[row, column] = entries.get((row, column), 0) + 2 * value
        return sp.SparseMatrix(len(target), len(source), entries)

    def verify(self, maximum_level: int = 4) -> None:
        for level in range(maximum_level + 1):
            d = self.dilation(level)
            for axis in range(DIMENSION):
                p = self.translation(axis, level)
                if self.dilation(level + 1) * p - p * d != p:
                    raise AssertionError("[D,P] != P")
                if level > 0:
                    k = self.special_conformal(axis, level)
                    if self.dilation(level - 1) * k - k * d != -k:
                        raise AssertionError("[D,K] != -K")
        for level in range(maximum_level):
            for first in range(DIMENSION):
                for second in range(DIMENSION):
                    k = self.special_conformal(first, level + 1)
                    p = self.translation(second, level)
                    left = k * p
                    if level > 0:
                        left -= self.translation(second, level - 1) * self.special_conformal(first, level)
                    right = 2 * int(first == second) * self.dilation(level)
                    if first != second:
                        ordered = tuple(sorted((first, second)))
                        orientation = 1 if first < second else -1
                        right -= 2 * orientation * self.rotation(*ordered, level)
                    if left != right:
                        raise AssertionError("[K,P] conformal bracket failed")
