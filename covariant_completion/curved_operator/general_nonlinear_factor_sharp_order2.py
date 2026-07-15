"""Exact order-two Schur gate for the sharp-reduced general factors.

The action-pairing adjoint reduces the complete problem to one product

``DP=(Box+A^-+B^-)(Box+A^++B^+)``.

Here ``D`` is self-adjoint, the right product is the formal adjoint of the
left product, and the exact cubic gate leaves 21 parameters for ``(X_1,S)``.
Writing ``A^-=U`` and ``A^+=S-U`` leaves 93 first-order split parameters.
The algebraic variables are a 24-dimensional self-adjoint ``X_0`` and two
38-dimensional invariant matrices ``B^-`` and ``B^+``.  Thus the complete
sharp-reduced ledger has 214 parameters.

At derivative order two the 100 algebraic variables enter linearly, while
the only nonlinear term is ``U(S-U)``.  This module assembles that exact
sparse PBW system and projects it to the cokernel of the algebraic-variable
matrix.  Orders one and zero are intentionally not inferred from this gate.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
from typing import Mapping

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .auxiliary_lower_order_factor_ansatz import (
    _coefficient_tuple,
    _field_first_order_invariance_matrix,
)
from .auxiliary_prenormal_symbol import AuxiliaryPrenormalSymbol
from .auxiliary_triangular_box_factor import (
    RowKey,
    _endomorphism,
    _field_operator_tables,
    _first_table,
    _zeroth_invariant_basis,
)
from .conventions import _ordinary_system
from .general_adjoint_factor import (
    _first_self_adjoint_basis,
    _unisolvent_cubic_points,
    _zeroth_self_adjoint_basis,
)
from .general_nonlinear_factor_system import (
    Monomial,
    Polynomial,
    SparseSystem,
    _clean_polynomial,
    _clean_system,
    _hash_system,
    _normalized_polynomial_bytes,
    _polynomial_bytes,
)
from .symmetrized_pbw_composition import SymmetrizedPBWComposer


VARIABLE_BLOCKS: tuple[tuple[str, int], ...] = (
    ("sharp_cubic_kernel", 21),
    ("left_first_order_split", 93),
    ("self_adjoint_X0", 24),
    ("B_L_minus", 38),
    ("B_L_plus", 38),
)


def _offsets() -> dict[str, range]:
    result: dict[str, range] = {}
    offset = 0
    for name, dimension in VARIABLE_BLOCKS:
        result[name] = range(offset, offset + dimension)
        offset += dimension
    if offset != 214:
        raise AssertionError("sharp order-two variable ledger drifted")
    return result


def _sharp_cubic_kernel(
    first_basis: sp.Matrix,
    first_self_coordinates: sp.Matrix,
) -> sp.Matrix:
    """Return the exact 137 by 21 kernel in ``(X_self,S)`` coordinates."""

    prenormal = AuxiliaryPrenormalSymbol.build()
    points, determinant = _unisolvent_cubic_points()
    if determinant != 3623878656:
        raise AssertionError("sharp cubic unisolvent determinant drifted")
    self_basis = first_basis * first_self_coordinates
    x_coefficients = tuple(
        _coefficient_tuple(self_basis[:, column])
        for column in range(self_basis.cols)
    )
    sum_coefficients = tuple(
        _coefficient_tuple(first_basis[:, column])
        for column in range(first_basis.cols)
    )
    entries: dict[tuple[int, int], sp.Expr] = {}
    for point_index, point in enumerate(points):
        substitutions = dict(zip(prenormal.covector, point, strict=True))
        principal = prenormal.field_principal_symbol.subs(substitutions)
        wave = prenormal.wave_quadratic.subs(substitutions)
        for column, coefficients in enumerate(x_coefficients):
            symbol = sum(
                (point[axis] * coefficients[axis] for axis in range(4)),
                sp.zeros(24),
            )
            for (row, input_), value in (symbol * principal).todok().items():
                entries[(point_index * 576 + row * 24 + input_, column)] = value
        for offset, coefficients in enumerate(sum_coefficients):
            symbol = sum(
                (point[axis] * coefficients[axis] for axis in range(4)),
                sp.zeros(24),
            )
            for (row, input_), value in (-wave * symbol).todok().items():
                entries[
                    (
                        point_index * 576 + row * 24 + input_,
                        len(x_coefficients) + offset,
                    )
                ] = value
    equations = sp.SparseMatrix(20 * 576, 44 + 93, entries)
    domain = DomainMatrix.from_Matrix(equations)
    if domain.rank() != 116:
        raise AssertionError("sharp cubic rank drifted")
    kernel = domain.nullspace().to_Matrix().T
    if kernel.shape != (137, 21):
        raise AssertionError("sharp cubic kernel drifted")
    return kernel


def _add_order_two(
    system: SparseSystem,
    monomial: Monomial,
    table: Mapping[tuple[int, ...], sp.Matrix],
    scale: sp.Expr = sp.Integer(1),
) -> None:
    monomial = tuple(sorted(monomial))
    for word, matrix in table.items():
        if len(word) != 2:
            continue
        for (row, column), value in matrix.todok().items():
            coefficient = sp.expand(scale * value)
            if coefficient == 0:
                continue
            key = ("DP", word, row, column)
            polynomial = system.setdefault(key, {})
            polynomial[monomial] = sp.expand(
                polynomial.get(monomial, 0) + coefficient
            )


@dataclass(frozen=True)
class GeneralNonlinearFactorSharpOrderTwo:
    equations: SparseSystem
    variable_offsets: Mapping[str, range]
    equation_rows: int
    monomial_occurrences_by_degree: tuple[int, ...]
    system_sha256: str
    linear_shape: tuple[int, int]
    linear_rank: int
    pivot_rows: tuple[int, ...]
    pivot_columns: tuple[int, ...]
    residual_term_count: int
    schur_constraint_count: int
    schur_unique_constraint_count: int
    schur_term_count: int
    schur_degree_counts: tuple[int, ...]
    schur_sha256: str
    constant_obstruction: bool
    projected_constraints: tuple[Polynomial, ...]

    @staticmethod
    def build() -> "GeneralNonlinearFactorSharpOrderTwo":
        pbw = SymmetrizedPBWComposer.build()
        field, complement, box = _field_operator_tables(pbw)
        pairing = _ordinary_system().field_fibre_pairing

        first_domain = DomainMatrix.from_Matrix(
            _field_first_order_invariance_matrix()
        )
        first_basis = first_domain.nullspace().to_Matrix().T
        if first_basis.shape != (2304, 93):
            raise AssertionError("first invariant basis drifted")
        first_self = _first_self_adjoint_basis(first_basis, pairing)
        if first_self.shape != (93, 44):
            raise AssertionError("first self-adjoint basis drifted")
        cubic_kernel = _sharp_cubic_kernel(first_basis, first_self)

        zeroth_basis = _zeroth_invariant_basis()
        zeroth_self = _zeroth_self_adjoint_basis(zeroth_basis, pairing)
        if zeroth_self.shape != (38, 24):
            raise AssertionError("zeroth self-adjoint basis drifted")
        offsets = _offsets()

        first_tables = tuple(
            _first_table(first_basis, sp.eye(93)[:, column])
            for column in range(93)
        )
        x_coordinates = first_self * cubic_kernel[:44, :]
        sum_coordinates = cubic_kernel[44:, :]
        x1_tables = tuple(
            _first_table(first_basis, x_coordinates[:, column])
            for column in range(21)
        )
        sum_tables = tuple(
            _first_table(first_basis, sum_coordinates[:, column])
            for column in range(21)
        )
        x0_coordinates = zeroth_basis * zeroth_self
        x0_tables = tuple(
            {(): _endomorphism(x0_coordinates[:, column])}
            for column in range(24)
        )
        b_tables = tuple(
            {(): _endomorphism(zeroth_basis[:, column])}
            for column in range(38)
        )

        system: SparseSystem = {}
        _add_order_two(system, (), pbw.compose(complement, field))
        _add_order_two(system, (), pbw.compose(box, box), -1)

        # D corrections.
        for variable, table in zip(
            offsets["sharp_cubic_kernel"], x1_tables, strict=True
        ):
            _add_order_two(system, (variable,), pbw.compose(table, field))
        for variable, table in zip(
            offsets["self_adjoint_X0"], x0_tables, strict=True
        ):
            _add_order_two(system, (variable,), pbw.compose(table, field))

        # Algebraic factor coefficients enter linearly at order two.
        for variable, table in zip(offsets["B_L_minus"], b_tables, strict=True):
            _add_order_two(system, (variable,), pbw.compose(table, box), -1)
        for variable, table in zip(offsets["B_L_plus"], b_tables, strict=True):
            _add_order_two(system, (variable,), pbw.compose(box, table), -1)

        # -U(S-U)=-US+U^2.  This is the complete nonlinear contribution at
        # derivative order two; Box-A terms have odd total derivative order.
        for split_variable, split_table in zip(
            offsets["left_first_order_split"], first_tables, strict=True
        ):
            for cubic_variable, sum_table in zip(
                offsets["sharp_cubic_kernel"], sum_tables, strict=True
            ):
                _add_order_two(
                    system,
                    (split_variable, cubic_variable),
                    pbw.compose(split_table, sum_table),
                    -1,
                )
            for inner_variable, inner_table in zip(
                offsets["left_first_order_split"], first_tables, strict=True
            ):
                _add_order_two(
                    system,
                    (split_variable, inner_variable),
                    pbw.compose(split_table, inner_table),
                    1,
                )
        system = _clean_system(system)

        algebraic_variables = tuple(
            variable
            for name in ("self_adjoint_X0", "B_L_minus", "B_L_plus")
            for variable in offsets[name]
        )
        rows = tuple(sorted(system))
        row_index = {key: index for index, key in enumerate(rows)}
        column_index = {
            variable: index for index, variable in enumerate(algebraic_variables)
        }
        entries: dict[tuple[int, int], sp.Expr] = {}
        residuals: list[Polynomial] = [dict() for _ in rows]
        residual_terms = 0
        for key in rows:
            for monomial, coefficient in system[key].items():
                if len(monomial) == 1 and monomial[0] in column_index:
                    entries[(row_index[key], column_index[monomial[0]])] = coefficient
                else:
                    if any(variable in column_index for variable in monomial):
                        raise AssertionError(
                            "algebraic variables entered nonlinearly at order two"
                        )
                    residuals[row_index[key]][monomial] = coefficient
                    residual_terms += 1
        linear = sp.SparseMatrix(len(rows), len(algebraic_variables), entries)
        rank = DomainMatrix.from_Matrix(linear).rank()
        _, pivot_rows_raw = DomainMatrix.from_Matrix(linear.T).rref()
        pivot_rows = tuple(int(item) for item in pivot_rows_raw)
        selected = linear[list(pivot_rows), :]
        _, pivot_columns_raw = DomainMatrix.from_Matrix(selected).rref()
        pivot_columns = tuple(int(item) for item in pivot_columns_raw)
        square = linear[list(pivot_rows), list(pivot_columns)]
        inverse = square.inv()

        selected_residuals = [residuals[row] for row in pivot_rows]
        pivot_row_set = set(pivot_rows)
        schur_digest = hashlib.sha256()
        normalized_constraints: dict[bytes, Polynomial] = {}
        constraint_count = 0
        schur_terms = 0
        schur_degrees = [0, 0, 0]
        constant_obstruction = False
        for row in range(len(rows)):
            if row in pivot_row_set:
                continue
            weights = linear[[row], list(pivot_columns)] * inverse
            constraint: dict[Monomial, sp.Expr] = defaultdict(
                lambda: sp.Integer(0)
            )
            for monomial, coefficient in residuals[row].items():
                constraint[monomial] += coefficient
            for selected_index in range(rank):
                weight = weights[selected_index]
                if weight == 0:
                    continue
                for monomial, coefficient in selected_residuals[
                    selected_index
                ].items():
                    constraint[monomial] -= weight * coefficient
            clean = _clean_polynomial(constraint)
            if not clean:
                continue
            constraint_count += 1
            schur_terms += len(clean)
            for monomial in clean:
                schur_degrees[len(monomial)] += 1
            schur_digest.update(f"row={row}\n".encode())
            schur_digest.update(_polynomial_bytes(clean))
            normalized = _normalized_polynomial_bytes(clean)
            first = clean[min(clean)]
            normalized_constraints[normalized] = {
                monomial: sp.cancel(value / first)
                for monomial, value in clean.items()
            }
            if set(clean) == {()}:
                constant_obstruction = True

        degree_counts = tuple(
            sum(
                len(monomial) == degree
                for polynomial in system.values()
                for monomial in polynomial
            )
            for degree in range(3)
        )
        result = GeneralNonlinearFactorSharpOrderTwo(
            equations=system,
            variable_offsets=offsets,
            equation_rows=len(rows),
            monomial_occurrences_by_degree=degree_counts,
            system_sha256=_hash_system(system),
            linear_shape=linear.shape,
            linear_rank=rank,
            pivot_rows=pivot_rows,
            pivot_columns=pivot_columns,
            residual_term_count=residual_terms,
            schur_constraint_count=constraint_count,
            schur_unique_constraint_count=len(normalized_constraints),
            schur_term_count=schur_terms,
            schur_degree_counts=tuple(schur_degrees),
            schur_sha256=schur_digest.hexdigest(),
            constant_obstruction=constant_obstruction,
            projected_constraints=tuple(
                normalized_constraints[key]
                for key in sorted(normalized_constraints)
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if tuple(
            (name, len(block)) for name, block in self.variable_offsets.items()
        ) != VARIABLE_BLOCKS:
            raise AssertionError("sharp order-two variable blocks drifted")
        if (
            self.equation_rows,
            self.monomial_occurrences_by_degree,
            self.system_sha256,
        ) != (
            1242,
            (318, 2942, 16926),
            "efe52303bf959a647a247acacacafc1d2d1eaee44e3b03ae340d5a70a867cce1",
        ):
            raise AssertionError("sharp order-two sparse system ledger drifted")
        if (self.linear_shape, self.linear_rank) != ((1242, 100), 52):
            raise AssertionError("sharp algebraic-variable rank drifted")
        if len(self.pivot_rows) != self.linear_rank:
            raise AssertionError("sharp pivot-row ledger drifted")
        if len(self.pivot_columns) != self.linear_rank:
            raise AssertionError("sharp pivot-column ledger drifted")
        if hashlib.sha256(
            repr(self.pivot_rows).encode()
        ).hexdigest() != "4b656bc15d88d7b6e1bca3852f09deebe0053f361107aa72423b07cf6f09c60f":
            raise AssertionError("sharp pivot-row hash drifted")
        if self.pivot_columns != (
            0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
            13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24,
            25, 26, 28, 29, 31, 32, 33, 34, 38, 39, 40, 41,
            42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53,
            54, 55, 59,
        ):
            raise AssertionError("sharp pivot-column ledger drifted")
        if (
            self.residual_term_count,
            self.schur_constraint_count,
            self.schur_unique_constraint_count,
            self.schur_term_count,
            self.schur_degree_counts,
            self.schur_sha256,
            self.constant_obstruction,
        ) != (
            17716,
            1050,
            179,
            24837,
            (189, 477, 24171),
            "85faed0c26fbe68b348f049271af708f53bc566ade91733312c1e85f60547b3a",
            False,
        ):
            raise AssertionError("sharp Schur projection ledger drifted")
        if len(self.projected_constraints) != 179:
            raise AssertionError("sharp projected polynomial retention drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-general-nonlinear-factor-sharp-order2-v1",
            "scope": {
                "pairing": "action pairing J_act",
                "left_equation": "DP=(Box+A^-+B^-)(Box+A^++B^+)",
                "right_equation": "formal adjoint; no independent variables",
                "right_factors": "R_-=L_+^sharp and R_+=L_-^sharp",
                "derivative_order": 2,
                "PBW_curvature_exact": True,
            },
            "variables": {
                name: {"offset": block.start, "dimension": len(block)}
                for name, block in self.variable_offsets.items()
            },
            "total_variables": 214,
            "sparse_order_two_system": {
                "equation_rows": self.equation_rows,
                "monomial_occurrences_by_degree_0_to_2": list(
                    self.monomial_occurrences_by_degree
                ),
                "content_sha256": self.system_sha256,
            },
            "algebraic_schur_gate": {
                "variables": ["self_adjoint_X0", "B_L_minus", "B_L_plus"],
                "variable_count": 100,
                "matrix_shape": list(self.linear_shape),
                "rank": self.linear_rank,
                "cokernel_dimension": self.linear_shape[0] - self.linear_rank,
                "free_algebraic_variables": 100 - self.linear_rank,
                "pivot_rows_sha256": hashlib.sha256(
                    repr(self.pivot_rows).encode()
                ).hexdigest(),
                "pivot_columns": list(self.pivot_columns),
                "residual_split_polynomial_terms": self.residual_term_count,
                "nonzero_projected_constraints": self.schur_constraint_count,
                "unique_constraints_up_to_scale": (
                    self.schur_unique_constraint_count
                ),
                "projected_term_count": self.schur_term_count,
                "projected_monomial_occurrences_by_degree_0_to_2": list(
                    self.schur_degree_counts
                ),
                "projected_content_sha256": self.schur_sha256,
                "constant_polynomial_obstruction": self.constant_obstruction,
                "projection_completed": True,
            },
            "outcome": {
                "sharp_reduced_order_two_system_exact": True,
                "order_two_solution_found": False,
                "order_two_obstruction_found": self.constant_obstruction,
                "orders_one_and_zero_solved": False,
                "general_factorization_proved": False,
                "general_factorization_disproved": False,
                "mixed_order_green_realization": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "the sharp-reduced 214-parameter factor branch is projected "
                "exactly through derivative order two.  Unless the projected "
                "system contains a constant contradiction, its remaining "
                "quadratic constraints and all orders one and zero remain open; "
                "no complete factorization or Green theorem follows"
            ),
        }
