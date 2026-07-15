"""Exact sparse coefficient system for the general mixed-order factors.

This module assembles the branch which remains after the simultaneous cubic
gate.  No factor is required to be the bare rough wave operator.  With

``D=D_naive+X_1+X_0``

the two products are parameterized as

``DP=(Box+A_L^-+B_L^-)(Box+A_L^++B_L^+)`` and
``PD=(Box+A_R^-+B_R^-)(Box+A_R^++B_R^+)``.

The cubic kernel fixes ``X_1`` and the sums ``A^-+A^+`` up to 45
parameters.  The two first-order splittings contribute 93 parameters each,
and the five invariant algebraic matrices contribute 38 parameters each:
421 variables in total.  Exact PBW composition shows that the complete
coefficient system is quadratic.  It is stored sparsely as

``(side, symmetric derivative word, output, input) -> polynomial``.

The fixed derivative-order-two coefficient matrix of the 190 algebraic
variables is also extracted.  This is the correct first Schur gate: all
remaining order-two dependence is quadratic only in the 231 cubic/splitting
variables.  The module deliberately does not infer a factorization from
assembly or from a specialized rank test.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import hashlib
from typing import Iterable, Mapping

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .auxiliary_triangular_box_factor import (
    RowKey,
    _endomorphism,
    _field_operator_tables,
    _first_table,
    _simultaneous_cubic_basis,
    _zeroth_invariant_basis,
)
from .symmetrized_pbw_composition import SymmetrizedPBWComposer


Monomial = tuple[int, ...]
Polynomial = dict[Monomial, sp.Expr]
SparseSystem = dict[RowKey, Polynomial]


VARIABLE_BLOCKS: tuple[tuple[str, int], ...] = (
    ("cubic_kernel", 45),
    ("left_first_order_split", 93),
    ("right_first_order_split", 93),
    ("X0", 38),
    ("B_L_minus", 38),
    ("B_L_plus", 38),
    ("B_R_minus", 38),
    ("B_R_plus", 38),
)


def _offsets() -> dict[str, range]:
    result: dict[str, range] = {}
    offset = 0
    for name, dimension in VARIABLE_BLOCKS:
        result[name] = range(offset, offset + dimension)
        offset += dimension
    if offset != 421:
        raise AssertionError("general factor variable ledger drifted")
    return result


def _add_polynomial_table(
    system: SparseSystem,
    side: str,
    monomial: Iterable[int],
    table: Mapping[tuple[int, ...], sp.Matrix],
    scale: sp.Expr = sp.Integer(1),
) -> None:
    canonical_monomial = tuple(sorted(monomial))
    for word, matrix in table.items():
        for (row, column), value in matrix.todok().items():
            coefficient = sp.expand(scale * value)
            if coefficient == 0:
                continue
            key = (side, word, row, column)
            polynomial = system.setdefault(key, {})
            polynomial[canonical_monomial] = sp.expand(
                polynomial.get(canonical_monomial, 0) + coefficient
            )


def _clean_system(system: SparseSystem) -> SparseSystem:
    result: SparseSystem = {}
    for key, polynomial in system.items():
        clean = {
            monomial: coefficient
            for monomial, value in polynomial.items()
            if (coefficient := sp.expand(value)) != 0
        }
        if clean:
            result[key] = clean
    return result


def _hash_system(system: SparseSystem) -> str:
    digest = hashlib.sha256()
    for key in sorted(system):
        side, word, row, column = key
        digest.update(f"{side}|{word}|{row}|{column}\n".encode())
        for monomial, coefficient in sorted(system[key].items()):
            digest.update(f"{monomial}|{sp.srepr(coefficient)}\n".encode())
    return digest.hexdigest()


def _clean_polynomial(polynomial: Mapping[Monomial, sp.Expr]) -> Polynomial:
    return {
        monomial: coefficient
        for monomial, value in polynomial.items()
        if (coefficient := sp.expand(value)) != 0
    }


def _polynomial_bytes(polynomial: Mapping[Monomial, sp.Expr]) -> bytes:
    return "".join(
        f"{monomial}|{sp.srepr(coefficient)}\n"
        for monomial, coefficient in sorted(polynomial.items())
    ).encode()


def _normalized_polynomial_bytes(polynomial: Mapping[Monomial, sp.Expr]) -> bytes:
    """Canonicalize a nonzero rational polynomial up to nonzero scale."""

    clean = _clean_polynomial(polynomial)
    if not clean:
        return b""
    first = clean[min(clean)]
    return _polynomial_bytes(
        {monomial: sp.cancel(value / first) for monomial, value in clean.items()}
    )


def _linear_form(
    variables: Iterable[int],
    tables: Iterable[Mapping[tuple[int, ...], sp.Matrix]],
    *,
    scale: sp.Expr = sp.Integer(1),
) -> tuple[tuple[Monomial, sp.Expr, Mapping[tuple[int, ...], sp.Matrix]], ...]:
    return tuple(
        ((variable,), scale, table)
        for variable, table in zip(variables, tables, strict=True)
    )


def _factor_product(
    pbw: SymmetrizedPBWComposer,
    system: SparseSystem,
    side: str,
    outer: tuple[tuple[Monomial, sp.Expr, Mapping], ...],
    inner: tuple[tuple[Monomial, sp.Expr, Mapping], ...],
) -> None:
    """Subtract one complete affine-factor product from ``system``."""

    for outer_monomial, outer_scale, outer_table in outer:
        for inner_monomial, inner_scale, inner_table in inner:
            _add_polynomial_table(
                system,
                side,
                outer_monomial + inner_monomial,
                pbw.compose(outer_table, inner_table),
                -outer_scale * inner_scale,
            )


@dataclass(frozen=True)
class GeneralNonlinearFactorSystem:
    equations: SparseSystem
    variable_offsets: Mapping[str, range]
    row_counts_by_order: tuple[int, ...]
    term_counts_by_order: tuple[int, ...]
    monomial_counts_by_degree: tuple[int, ...]
    hashes_by_order: tuple[str, ...]
    quadratic_linear_shape: tuple[int, int]
    quadratic_linear_rank: int
    quadratic_linear_pivot_rows: tuple[int, ...]
    quadratic_linear_pivot_columns: tuple[int, ...]
    quadratic_residual_term_count: int
    quadratic_schur_constraint_count: int
    quadratic_schur_unique_constraint_count: int
    quadratic_schur_term_count: int
    quadratic_schur_degree_counts: tuple[int, ...]
    quadratic_schur_sha256: str
    quadratic_constant_obstruction: bool

    @staticmethod
    def build() -> "GeneralNonlinearFactorSystem":
        pbw = SymmetrizedPBWComposer.build()
        field, complement, box = _field_operator_tables(pbw)
        first_basis, cubic_kernel = _simultaneous_cubic_basis()
        zeroth_basis = _zeroth_invariant_basis()
        offsets = _offsets()

        first_basis_tables = tuple(
            _first_table(first_basis, sp.eye(93)[:, column])
            for column in range(93)
        )
        cubic_tables = tuple(
            tuple(
                _first_table(
                    first_basis,
                    cubic_kernel[block * 93 : (block + 1) * 93, column],
                )
                for column in range(45)
            )
            for block in range(3)
        )
        x1_tables, left_sum_tables, right_sum_tables = cubic_tables
        zeroth_tables = tuple(
            {(): _endomorphism(zeroth_basis[:, column])}
            for column in range(38)
        )

        system: SparseSystem = {}

        # D o P and P o D.
        _add_polynomial_table(system, "DP", (), pbw.compose(complement, field))
        _add_polynomial_table(system, "PD", (), pbw.compose(field, complement))
        for variable, table in zip(
            offsets["cubic_kernel"], x1_tables, strict=True
        ):
            _add_polynomial_table(
                system, "DP", (variable,), pbw.compose(table, field)
            )
            _add_polynomial_table(
                system, "PD", (variable,), pbw.compose(field, table)
            )
        for variable, table in zip(offsets["X0"], zeroth_tables, strict=True):
            _add_polynomial_table(
                system, "DP", (variable,), pbw.compose(table, field)
            )
            _add_polynomial_table(
                system, "PD", (variable,), pbw.compose(field, table)
            )

        # Affine factor ledgers.  A^+=S-A^- is represented without symbolic
        # matrices, so every composition remains an exact sparse PBW table.
        box_term = (((), sp.Integer(1), box),)
        left_outer = (
            box_term
            + _linear_form(offsets["left_first_order_split"], first_basis_tables)
            + _linear_form(offsets["B_L_minus"], zeroth_tables)
        )
        left_inner = (
            box_term
            + _linear_form(offsets["cubic_kernel"], left_sum_tables)
            + _linear_form(
                offsets["left_first_order_split"],
                first_basis_tables,
                scale=-1,
            )
            + _linear_form(offsets["B_L_plus"], zeroth_tables)
        )
        right_outer = (
            box_term
            + _linear_form(offsets["right_first_order_split"], first_basis_tables)
            + _linear_form(offsets["B_R_minus"], zeroth_tables)
        )
        right_inner = (
            box_term
            + _linear_form(offsets["cubic_kernel"], right_sum_tables)
            + _linear_form(
                offsets["right_first_order_split"],
                first_basis_tables,
                scale=-1,
            )
            + _linear_form(offsets["B_R_plus"], zeroth_tables)
        )
        _factor_product(pbw, system, "DP", left_outer, left_inner)
        _factor_product(pbw, system, "PD", right_outer, right_inner)
        system = _clean_system(system)

        orders = tuple(range(5))
        row_counts = tuple(
            sum(len(key[1]) == order for key in system) for order in orders
        )
        term_counts = tuple(
            sum(
                len(polynomial)
                for key, polynomial in system.items()
                if len(key[1]) == order
            )
            for order in orders
        )
        degree_counts = tuple(
            sum(
                len(monomial) == degree
                for polynomial in system.values()
                for monomial in polynomial
            )
            for degree in range(3)
        )
        hashes = tuple(
            _hash_system(
                {
                    key: polynomial
                    for key, polynomial in system.items()
                    if len(key[1]) == order
                }
            )
            for order in orders
        )

        # Fixed linear Schur matrix at derivative order two.  The remaining
        # polynomial includes only the 231 cubic/splitting variables.
        algebraic_variables = tuple(
            variable
            for name in ("X0", "B_L_minus", "B_L_plus", "B_R_minus", "B_R_plus")
            for variable in offsets[name]
        )
        rows = tuple(sorted(key for key in system if len(key[1]) == 2))
        row_index = {key: index for index, key in enumerate(rows)}
        column_index = {
            variable: index for index, variable in enumerate(algebraic_variables)
        }
        entries: dict[tuple[int, int], sp.Expr] = {}
        residual_terms = 0
        residuals: list[Polynomial] = [dict() for _ in rows]
        for key in rows:
            for monomial, coefficient in system[key].items():
                if len(monomial) == 1 and monomial[0] in column_index:
                    entries[(row_index[key], column_index[monomial[0]])] = coefficient
                else:
                    if any(variable in column_index for variable in monomial):
                        raise AssertionError(
                            "an algebraic variable entered nonlinearly at order two"
                        )
                    residuals[row_index[key]][monomial] = coefficient
                    residual_terms += 1
        linear = sp.SparseMatrix(len(rows), len(algebraic_variables), entries)
        linear_domain = DomainMatrix.from_Matrix(linear)
        rank = linear_domain.rank()
        _, pivot_rows = DomainMatrix.from_Matrix(linear.T).rref()
        selected = linear[list(pivot_rows), :]
        _, pivot_columns = DomainMatrix.from_Matrix(selected).rref()

        # Exact Schur projection to the cokernel of the fixed linear matrix.
        # The 100 selected rows and columns form an invertible square block.
        # A_i = weights_i A_selected, so consistency is exactly
        # r_i-weights_i r_selected=0.  Hashing the resulting sparse
        # polynomials makes this large intermediate reusable without emitting
        # tens of thousands of coefficient entries into JSON.
        pivot_rows_tuple = tuple(int(item) for item in pivot_rows)
        pivot_columns_tuple = tuple(int(item) for item in pivot_columns)
        square = linear[list(pivot_rows_tuple), list(pivot_columns_tuple)]
        inverse = square.inv()
        selected_residuals = [residuals[row] for row in pivot_rows_tuple]
        pivot_row_set = set(pivot_rows_tuple)
        schur_digest = hashlib.sha256()
        normalized_constraints: set[bytes] = set()
        constraint_count = 0
        schur_term_count = 0
        schur_degree_counts = [0, 0, 0]
        constant_obstruction = False
        for row in range(len(rows)):
            if row in pivot_row_set:
                continue
            weights = linear[[row], list(pivot_columns_tuple)] * inverse
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
            clean_constraint = _clean_polynomial(constraint)
            if not clean_constraint:
                continue
            constraint_count += 1
            schur_term_count += len(clean_constraint)
            for monomial in clean_constraint:
                schur_degree_counts[len(monomial)] += 1
            encoded = _polynomial_bytes(clean_constraint)
            schur_digest.update(f"row={row}\n".encode())
            schur_digest.update(encoded)
            normalized_constraints.add(
                _normalized_polynomial_bytes(clean_constraint)
            )
            if set(clean_constraint) == {()}:
                constant_obstruction = True

        result = GeneralNonlinearFactorSystem(
            equations=system,
            variable_offsets=offsets,
            row_counts_by_order=row_counts,
            term_counts_by_order=term_counts,
            monomial_counts_by_degree=degree_counts,
            hashes_by_order=hashes,
            quadratic_linear_shape=linear.shape,
            quadratic_linear_rank=rank,
            quadratic_linear_pivot_rows=pivot_rows_tuple,
            quadratic_linear_pivot_columns=pivot_columns_tuple,
            quadratic_residual_term_count=residual_terms,
            quadratic_schur_constraint_count=constraint_count,
            quadratic_schur_unique_constraint_count=len(normalized_constraints),
            quadratic_schur_term_count=schur_term_count,
            quadratic_schur_degree_counts=tuple(schur_degree_counts),
            quadratic_schur_sha256=schur_digest.hexdigest(),
            quadratic_constant_obstruction=constant_obstruction,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if tuple(
            (name, len(block)) for name, block in self.variable_offsets.items()
        ) != VARIABLE_BLOCKS:
            raise AssertionError("general nonlinear variable blocks drifted")
        if self.row_counts_by_order != (240, 960, 2484, 0, 0):
            raise AssertionError("general nonlinear equation-row ledger drifted")
        if self.term_counts_by_order != (4945, 16263, 38531, 0, 0):
            raise AssertionError("general nonlinear sparse-term ledger drifted")
        if self.monomial_counts_by_degree != (953, 8158, 50628):
            raise AssertionError("general nonlinear polynomial-degree ledger drifted")
        if self.hashes_by_order != (
            "968b990b01ca85171146e7d910d117a45fec4f0aa7d6f5c9aafb1dac6d61c2ff",
            "c8649eeeef9033a48963252a1bd4cfc079e896008dc34e46bce5c2cfceeceee6",
            "de1da6b876effbe0ede63ba989a69c6d190d966744eb357ccc3402fb0bd3c7bf",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        ):
            raise AssertionError("general nonlinear content hashes drifted")
        if (self.quadratic_linear_shape, self.quadratic_linear_rank) != (
            (2484, 190),
            100,
        ):
            raise AssertionError("quadratic Schur linear rank ledger drifted")
        if len(self.quadratic_linear_pivot_rows) != self.quadratic_linear_rank:
            raise AssertionError("quadratic Schur pivot-row ledger drifted")
        if len(self.quadratic_linear_pivot_columns) != self.quadratic_linear_rank:
            raise AssertionError("quadratic Schur pivot-column ledger drifted")
        if hashlib.sha256(
            repr(self.quadratic_linear_pivot_rows).encode()
        ).hexdigest() != "cc6c9078b08af5103f93db1f5bc512bccb250358d1df8254ff8b9322abccfba0":
            raise AssertionError("quadratic Schur pivot-row hash drifted")
        if self.quadratic_residual_term_count != 34340:
            raise AssertionError("quadratic Schur residual ledger drifted")
        if (
            self.quadratic_schur_constraint_count,
            self.quadratic_schur_unique_constraint_count,
            self.quadratic_schur_term_count,
            self.quadratic_schur_degree_counts,
            self.quadratic_schur_sha256,
            self.quadratic_constant_obstruction,
        ) != (
            2130,
            365,
            52119,
            (363, 1188, 50568),
            "3b57306ec54db2f927be135dd84c4a230b980655d4d44c51376503c746ccafab",
            False,
        ):
            raise AssertionError("quadratic Schur projection ledger drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-general-nonlinear-mixed-order-factor-system-v1",
            "ansatz": {
                "left": "DP=(Box+A_L^-+B_L^-)(Box+A_L^++B_L^+)",
                "right": "PD=(Box+A_R^-+B_R^-)(Box+A_R^++B_R^+)",
                "first_order_sums": "the exact 45-dimensional simultaneous cubic kernel",
                "variables": {
                    name: {"offset": block.start, "dimension": len(block)}
                    for name, block in self.variable_offsets.items()
                },
                "total_variables": 421,
                "PBW_curvature_exact": True,
            },
            "sparse_system": {
                "row_counts_by_derivative_order_0_to_4": list(self.row_counts_by_order),
                "term_counts_by_derivative_order_0_to_4": list(self.term_counts_by_order),
                "monomial_occurrences_by_degree_0_to_2": list(self.monomial_counts_by_degree),
                "content_sha256_by_derivative_order_0_to_4": list(self.hashes_by_order),
                "maximum_polynomial_degree": 2,
            },
            "quadratic_order_schur_gate": {
                "linear_variables": ["X0", "B_L_minus", "B_L_plus", "B_R_minus", "B_R_plus"],
                "linear_variable_count": 190,
                "matrix_shape": list(self.quadratic_linear_shape),
                "rank": self.quadratic_linear_rank,
                "cokernel_dimension": self.quadratic_linear_shape[0] - self.quadratic_linear_rank,
                "residual_constant_or_split_polynomial_terms": self.quadratic_residual_term_count,
                "pivot_rows_sha256": hashlib.sha256(repr(self.quadratic_linear_pivot_rows).encode()).hexdigest(),
                "pivot_columns": list(self.quadratic_linear_pivot_columns),
                "exact_schur_elimination_feasible": True,
                "determined_linear_variables": self.quadratic_linear_rank,
                "free_algebraic_variables_after_order_two": (
                    190 - self.quadratic_linear_rank
                ),
                "schur_polynomial_projection_completed": True,
                "nonzero_projected_constraints": self.quadratic_schur_constraint_count,
                "unique_constraints_up_to_scale": self.quadratic_schur_unique_constraint_count,
                "projected_term_count": self.quadratic_schur_term_count,
                "projected_monomial_occurrences_by_degree_0_to_2": list(
                    self.quadratic_schur_degree_counts
                ),
                "projected_content_sha256": self.quadratic_schur_sha256,
                "constant_polynomial_obstruction": self.quadratic_constant_obstruction,
                "pure_split_only_reduction_available": False,
                "reason_free_algebraic_variables_remain": (
                    "the fixed order-two linear matrix has rank 100, leaving "
                    "90 algebraic variables; at orders one and zero the B "
                    "blocks also occur bilinearly in A B and B B products"
                ),
            },
            "outcome": {
                "complete_421_variable_system_assembled": True,
                "order_two_schur_projection_completed": True,
                "exact_solution_found": False,
                "exact_obstruction_found": False,
                "mixed_order_factorization_proved": False,
                "green_realization_proved": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "the complete general two-nontrivial-factor coefficient system is "
                "assembled exactly as a sparse quadratic PBW system.  The fixed "
                "order-two algebraic-variable Schur gate is classified, but its "
                "polynomial cokernel equations and the lower-order equations have "
                "not yet been solved; no factorization or Green theorem follows"
            ),
        }
