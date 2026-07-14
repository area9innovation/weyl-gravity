"""Residual conformal module induced from the raw polynomial BV complex."""

from __future__ import annotations

from dataclasses import dataclass

import sympy as sp

from bridge.cyclic_retract import RawPolynomialRetraction
from bridge.residual_bfv import ConformalCE


def _rectangular_insert(
    target: sp.MutableSparseMatrix,
    block: sp.MatrixBase,
    row: int,
    column: int,
) -> None:
    target[row : row + block.rows, column : column + block.cols] = block


@dataclass(frozen=True)
class RawResidualModule:
    """Finite positive-energy buffer transferred from metric BV rows.

    ``K+`` is minus the coordinate special-conformal vector field.  This is
    the sign matching the residual-BFV convention
    ``[K+_a,K-_b]=2 delta_ab D+2 R_ab``; ``K-`` is coordinate translation.
    """

    maximum_energy: int
    retracts: dict[int, RawPolynomialRetraction]
    offsets: dict[int, int]
    dimensions: dict[int, int]
    matrices: tuple[sp.SparseMatrix, ...]
    state_energies: tuple[int, ...]

    @classmethod
    def build(cls, maximum_energy: int = 4) -> "RawResidualModule":
        if maximum_energy < 3:
            raise ValueError("need at least one noncompact buffer shell")
        retracts = {
            energy: RawPolynomialRetraction.build(energy)
            for energy in range(2, maximum_energy + 1)
        }
        offsets: dict[int, int] = {}
        dimensions: dict[int, int] = {}
        cursor = 0
        for energy, retract in retracts.items():
            offsets[energy] = cursor
            dimensions[energy] = retract.cohomology_dimension
            cursor += retract.cohomology_dimension

        ce = ConformalCE.build()
        matrices = [sp.MutableSparseMatrix(cursor, cursor, {}) for _ in ce.names]

        for energy, retract in retracts.items():
            offset = offsets[energy]
            dimension = dimensions[energy]
            matrices[ce.index["D"]][
                offset : offset + dimension, offset : offset + dimension
            ] = energy * sp.eye(dimension)
            for first in range(4):
                for second in range(first + 1, 4):
                    name = f"R{first}{second}"
                    induced = retract.induced(
                        retract.block.rotation(first, second), retract
                    )
                    _rectangular_insert(
                        matrices[ce.index[name]], induced, offset, offset
                    )
        for energy, source in retracts.items():
            source_offset = offsets[energy]
            if energy - 1 in retracts:
                target = retracts[energy - 1]
                target_offset = offsets[energy - 1]
                for axis in range(4):
                    operator = source.block.translation_to(target.block, axis)
                    induced = source.induced(operator, target)
                    _rectangular_insert(
                        matrices[ce.index[f"K-_{axis}"]],
                        induced,
                        target_offset,
                        source_offset,
                    )
            if energy + 1 in retracts:
                target = retracts[energy + 1]
                target_offset = offsets[energy + 1]
                for axis in range(4):
                    operator = source.block.special_to(target.block, axis)
                    induced = -source.induced(operator, target)
                    _rectangular_insert(
                        matrices[ce.index[f"K+_{axis}"]],
                        induced,
                        target_offset,
                        source_offset,
                    )

        result = cls(
            maximum_energy=maximum_energy,
            retracts=retracts,
            offsets=offsets,
            dimensions=dimensions,
            matrices=tuple(sp.SparseMatrix(matrix) for matrix in matrices),
            state_energies=tuple(
                energy
                for energy in range(2, maximum_energy + 1)
                for _ in range(dimensions[energy])
            ),
        )
        result.verify()
        return result

    @property
    def dimension(self) -> int:
        return len(self.state_energies)

    def indices_at(self, energy: int) -> tuple[int, ...]:
        start = self.offsets[energy]
        return tuple(range(start, start + self.dimensions[energy]))

    def verify(self) -> None:
        ce = ConformalCE.build()
        if tuple(self.dimensions.values())[:3] != (10, 40, 82):
            raise AssertionError("transferred buffer has the wrong first levels")
        interior = tuple(
            index
            for index, energy in enumerate(self.state_energies)
            if energy <= self.maximum_energy - 1
        )
        for first, left in enumerate(self.matrices):
            for second, right in enumerate(self.matrices):
                bracket = left * right - right * left
                expected = sp.zeros(self.dimension, self.dimension)
                for target, coefficient in enumerate(
                    ce.structure_constants[first][second]
                ):
                    if coefficient:
                        expected += coefficient * self.matrices[target]
                if bracket[:, list(interior)] != expected[:, list(interior)]:
                    raise AssertionError(
                        f"transferred conformal bracket failed for "
                        f"{ce.names[first]},{ce.names[second]}"
                    )
