"""Block-sparse exact solver for the arity-two Cartan complex.

The ambient bilinear-map complex grows cubically with the basis dimension.
When ``q1`` preserves declared additive labels (for example D weight, momentum,
jet filtration, or representation charge), ``[q1,-]`` preserves the label
defect ``w_out-w_left-w_right``.  This module partitions both source and target
coordinates by that defect and performs sparse rational elimination only in
blocks occupied by the Cartan source.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Sequence

try:
    from .arity_two_cartan import ArityTwoComplex, BilinearOperator
except ImportError:
    from arity_two_cartan import ArityTwoComplex, BilinearOperator


def _fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, bool):
        raise ValueError("block labels must be exact")
    return value if isinstance(value, Fraction) else Fraction(value)


def _clean(row: dict[int, Fraction]) -> dict[int, Fraction]:
    return {column: value for column, value in row.items() if value}


def sparse_rref_solve(
    rows: Sequence[dict[int, Fraction]],
    rhs: Sequence[Fraction],
    variable_count: int,
) -> tuple[Fraction, ...] | None:
    """Solve an exact sparse system with deterministic zero free variables."""

    if len(rows) != len(rhs):
        raise ValueError("sparse system row and rhs counts differ")
    augmented = [(_clean(dict(row)), _fraction(value)) for row, value in zip(rows, rhs)]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(variable_count):
        selected = next(
            (index for index in range(pivot_row, len(augmented)) if augmented[index][0].get(column)),
            None,
        )
        if selected is None:
            continue
        augmented[pivot_row], augmented[selected] = augmented[selected], augmented[pivot_row]
        row, value = augmented[pivot_row]
        pivot = row[column]
        row = {key: coefficient / pivot for key, coefficient in row.items()}
        value /= pivot
        augmented[pivot_row] = (row, value)
        for index, (other, other_value) in enumerate(augmented):
            if index == pivot_row or not other.get(column):
                continue
            factor = other[column]
            updated = dict(other)
            for key, coefficient in row.items():
                updated[key] = updated.get(key, Fraction(0)) - factor * coefficient
            augmented[index] = (_clean(updated), other_value - factor * value)
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(augmented):
            break
    if any(not row and value for row, value in augmented):
        return None
    solution = [Fraction(0) for _ in range(variable_count)]
    for index, column in enumerate(pivots):
        solution[column] = augmented[index][1]
    return tuple(solution)


@dataclass(frozen=True)
class BlockSparseArityTwoComplex:
    """An arity-two complex split by conserved additive basis labels."""

    ambient: ArityTwoComplex
    axis_names: tuple[str, ...]
    basis_labels: tuple[tuple[Fraction, ...], ...]

    def __post_init__(self) -> None:
        if not self.axis_names or len(set(self.axis_names)) != len(self.axis_names):
            raise ValueError("block decomposition needs unique named axes")
        if len(self.basis_labels) != self.ambient.dimension:
            raise ValueError("block labels do not match the ambient basis")
        width = len(self.axis_names)
        normalized = tuple(
            tuple(_fraction(value) for value in label)
            for label in self.basis_labels
        )
        if any(len(label) != width for label in normalized):
            raise ValueError("block label width differs from the axis ledger")
        object.__setattr__(self, "basis_labels", normalized)
        for output in range(self.ambient.dimension):
            for input_ in range(self.ambient.dimension):
                if self.ambient.q1.entries[output][input_] and normalized[output] != normalized[input_]:
                    raise ValueError("q1 does not preserve the declared block labels")

    @property
    def q1(self):
        return self.ambient.q1

    def validate_bilinear(self, operator: BilinearOperator) -> None:
        self.ambient.validate_bilinear(operator)

    def differential(self, operator: BilinearOperator, *, name: str) -> BilinearOperator:
        return self.ambient.differential(operator, name=name)

    def _slot_key(self, slot: tuple[int, int, int]) -> tuple[Fraction, ...]:
        output, left, right = slot
        return tuple(
            self.basis_labels[output][axis]
            - self.basis_labels[left][axis]
            - self.basis_labels[right][axis]
            for axis in range(len(self.axis_names))
        )

    def coordinate_partitions(self, degree: int) -> dict[tuple[Fraction, ...], tuple[int, ...]]:
        grouped: dict[tuple[Fraction, ...], list[int]] = {}
        for index, slot in enumerate(self.ambient.coordinate_slots(degree)):
            grouped.setdefault(self._slot_key(slot), []).append(index)
        return {key: tuple(grouped[key]) for key in sorted(grouped)}

    def _block_matrix(
        self,
        *,
        source_degree: int,
        key: tuple[Fraction, ...],
    ) -> tuple[tuple[int, ...], tuple[int, ...], tuple[dict[int, Fraction], ...], int]:
        source_indices = self.coordinate_partitions(source_degree).get(key, ())
        target_indices = self.coordinate_partitions(source_degree + 1).get(key, ())
        rows = [dict() for _ in target_indices]
        nonzero_count = 0
        source_slot_count = len(self.ambient.coordinate_slots(source_degree))
        for local_column, ambient_column in enumerate(source_indices):
            coordinates = [Fraction(0) for _ in range(source_slot_count)]
            coordinates[ambient_column] = Fraction(1)
            basis = self.ambient.operator_from_coordinates(
                source_degree,
                coordinates,
                name=f"block_basis_{source_degree}_{ambient_column}",
            )
            image = self.ambient.coordinates(
                self.ambient.differential(basis, name="delta_block_basis")
            )
            for local_row, ambient_row in enumerate(target_indices):
                value = image[ambient_row]
                if value:
                    rows[local_row][local_column] = value
                    nonzero_count += 1
            if any(image[index] for index in range(len(image)) if index not in target_indices):
                raise AssertionError("q1 differential escaped a conserved-label block")
        return source_indices, target_indices, tuple(rows), nonzero_count

    def solve_boundary(self, target: BilinearOperator) -> BilinearOperator | None:
        self.validate_bilinear(target)
        target_coordinates = self.ambient.coordinates(target)
        source_degree = target.degree - 1
        source_coordinates = [Fraction(0) for _ in self.ambient.coordinate_slots(source_degree)]
        target_partitions = self.coordinate_partitions(target.degree)
        for key, target_indices in target_partitions.items():
            rhs = tuple(target_coordinates[index] for index in target_indices)
            if not any(rhs):
                continue
            source_indices, verified_target_indices, rows, _nonzero = self._block_matrix(
                source_degree=source_degree,
                key=key,
            )
            if verified_target_indices != target_indices:
                raise AssertionError("block target partition drifted")
            solution = sparse_rref_solve(rows, rhs, len(source_indices))
            if solution is None:
                return None
            for index, value in zip(source_indices, solution):
                source_coordinates[index] = value
        primitive = self.ambient.operator_from_coordinates(
            source_degree,
            source_coordinates,
            name=f"block_sparse_primitive_for_{target.name}",
        )
        if self.ambient.differential(primitive, name="delta_block_primitive").entries != target.entries:
            raise AssertionError("block-sparse solver returned an invalid primitive")
        return primitive

    def dual_nontriviality_witness(self, cocycle: BilinearOperator) -> tuple[Fraction, ...]:
        self.validate_bilinear(cocycle)
        coordinates = self.ambient.coordinates(cocycle)
        for key, target_indices in self.coordinate_partitions(cocycle.degree).items():
            target = tuple(coordinates[index] for index in target_indices)
            if not any(target):
                continue
            source_indices, _verified, matrix_rows, _nonzero = self._block_matrix(
                source_degree=cocycle.degree - 1,
                key=key,
            )
            boundary_columns = [
                {
                    local_row: matrix_rows[local_row][local_column]
                    for local_row in range(len(target_indices))
                    if local_column in matrix_rows[local_row]
                }
                for local_column in range(len(source_indices))
            ]
            equations = boundary_columns + [
                {index: value for index, value in enumerate(target) if value}
            ]
            rhs = [Fraction(0) for _ in boundary_columns] + [Fraction(1)]
            local_witness = sparse_rref_solve(equations, rhs, len(target_indices))
            if local_witness is None:
                continue
            witness = [Fraction(0) for _ in coordinates]
            for ambient_index, value in zip(target_indices, local_witness):
                witness[ambient_index] = value
            return tuple(witness)
        raise ValueError("no normalized block-sparse obstruction witness exists")

    def metrics(self, target_degree: int) -> dict[str, object]:
        source_partitions = self.coordinate_partitions(target_degree - 1)
        target_partitions = self.coordinate_partitions(target_degree)
        shared = sorted(set(source_partitions) | set(target_partitions))
        nonzero_coefficients = 0
        for key in shared:
            _source, _target, _rows, count = self._block_matrix(
                source_degree=target_degree - 1,
                key=key,
            )
            nonzero_coefficients += count
        return {
            "axis_names": list(self.axis_names),
            "source_coordinate_count": sum(len(indices) for indices in source_partitions.values()),
            "target_coordinate_count": sum(len(indices) for indices in target_partitions.values()),
            "block_count": len(shared),
            "largest_source_block": max((len(indices) for indices in source_partitions.values()), default=0),
            "largest_target_block": max((len(indices) for indices in target_partitions.values()), default=0),
            "differential_nonzero_coefficient_count": nonzero_coefficients,
        }
