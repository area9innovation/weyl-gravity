"""Sparse Chevalley--Eilenberg complexes with a graded coefficient module."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import TypeAlias

import sympy as sp
from sympy.polys.domains import GF
from sympy.polys.matrices import DomainMatrix

from bridge.residual_bfv.conformal_ce import ConformalCE, Monomial


SparseVector: TypeAlias = dict[int, sp.Expr]


def _add(output: dict, key, value) -> None:
    value = sp.cancel(value)
    if value == 0:
        return
    output[key] = sp.cancel(output.get(key, 0) + value)
    if output[key] == 0:
        del output[key]


def _wedge(first: Monomial, second: Monomial):
    if set(first).intersection(second):
        return None
    inversions = sum(left > right for left in first for right in second)
    return (-1 if inversions % 2 else 1), tuple(sorted(first + second))


@dataclass(frozen=True)
class CoefficientModule:
    matrices: tuple[sp.MatrixBase, ...]
    state_energies: tuple[int, ...]

    @property
    def dimension(self) -> int:
        return len(self.state_energies)


@dataclass(frozen=True)
class CoefficientCEComplex:
    ce: ConformalCE
    module: CoefficientModule

    def basis(self, ghost_number: int, total_degree: int = 0):
        states_by_energy: dict[int, list[int]] = {}
        for state, energy in enumerate(self.module.state_energies):
            states_by_energy.setdefault(energy, []).append(state)
        output = []
        for monomial in combinations(range(self.ce.dimension), ghost_number):
            matter_energy = total_degree - self.ce.compact_degree(monomial)
            output.extend(
                (monomial, state)
                for state in states_by_energy.get(matter_energy, ())
            )
        return tuple(output)

    def differential(self, source, target) -> tuple[SparseVector, ...]:
        target_index = {basis: index for index, basis in enumerate(target)}
        output: list[SparseVector] = []
        for monomial, state in source:
            image: SparseVector = {}
            for position, ghost in enumerate(monomial):
                prefix = monomial[:position]
                suffix = monomial[position + 1 :]
                for pair, coefficient in self.ce.ghost_differentials[ghost].items():
                    first = _wedge(prefix, pair)
                    if first is None:
                        continue
                    sign_first, partial = first
                    second = _wedge(partial, suffix)
                    if second is None:
                        continue
                    sign_second, result = second
                    key = (result, state)
                    if key not in target_index:
                        raise AssertionError("ghost differential left the grading window")
                    _add(
                        image,
                        target_index[key],
                        (-1) ** position
                        * sign_first
                        * sign_second
                        * coefficient,
                    )

            for ghost, matrix in enumerate(self.module.matrices):
                product = _wedge((ghost,), monomial)
                if product is None:
                    continue
                sign, result_monomial = product
                for result_state in range(matrix.rows):
                    coefficient = matrix[result_state, state]
                    if coefficient == 0:
                        continue
                    key = (result_monomial, result_state)
                    if key not in target_index:
                        raise AssertionError("module action left the grading window")
                    _add(image, target_index[key], sign * coefficient)
            output.append(image)
        return tuple(output)


def compose(first: tuple[SparseVector, ...], second: tuple[SparseVector, ...]):
    output: list[SparseVector] = []
    for column in first:
        result: SparseVector = {}
        for middle, first_value in column.items():
            for row, second_value in second[middle].items():
                _add(result, row, first_value * second_value)
        output.append(result)
    return tuple(output)


def columns_to_matrix(columns: tuple[SparseVector, ...], rows: int) -> sp.SparseMatrix:
    return sp.SparseMatrix(
        rows,
        len(columns),
        {
            (row, column): value
            for column, vector in enumerate(columns)
            for row, value in vector.items()
        },
    )


def modular_value(value: sp.Expr, prime: int) -> int:
    value = sp.cancel(value)
    if not value.is_Rational:
        raise ValueError(f"non-rational transferred coefficient {value}")
    return int(value.p) * pow(int(value.q), -1, prime) % prime


def modular_rank(
    columns: tuple[SparseVector, ...], rows: int, prime: int = 1009
) -> int:
    row_data: dict[int, dict[int, int]] = {}
    for column, vector in enumerate(columns):
        for row, value in vector.items():
            reduced = modular_value(value, prime)
            if reduced:
                row_data.setdefault(row, {})[column] = reduced
    matrix = DomainMatrix.from_dict_sympy(rows, len(columns), row_data).convert_to(
        GF(prime)
    )
    return matrix.rank()
