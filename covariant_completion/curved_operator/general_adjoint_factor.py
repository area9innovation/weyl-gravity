"""Pairing-aware reduction of the general mixed-order factor problem.

This module imposes the action pairing and the natural formal-adjoint
relations before attempting the nonlinear lower-order factor equations.  It
does *not* transpose the coefficient matrices of an ordered-word table.  The
operator is first reduced to the unique symmetrized covariant-jet/PBW table;
only there do the matrices form the components of one parallel coefficient
tensor and admit the coefficientwise action-pairing adjoint

``(A^I nabla_(I))^sharp=(-1)^|I| J^-1 (A^I)^T J nabla_(I)``.

For the exact self-adjoint field operator ``P`` we choose a self-adjoint
complement ``D``.  Hence a left factorization

``D P=L_- L_+``

automatically gives the right factorization

``P D=R_- R_+``, ``R_-=L_+^sharp``, ``R_+=L_-^sharp``.

The calculation below determines the complete invariant dimensions after
these sharp constraints and solves the exact cubic gate.  The remaining
quadratic, linear and algebraic equations are nonlinear and are deliberately
left open; no factorization or Green theorem is inferred.
"""

from __future__ import annotations

from dataclasses import dataclass
import gc
from itertools import product
from typing import Mapping

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .auxiliary_lower_order_factor_ansatz import (
    _coefficient_tuple,
    _field_first_order_invariance_matrix,
)
from .auxiliary_prenormal_symbol import AuxiliaryPrenormalSymbol
from .auxiliary_triangular_box_factor import (
    _endomorphism,
    _field_operator_tables,
    _zeroth_invariant_basis,
)
from .conventions import _ordinary_system
from .parallel_operator_composition import (
    OperatorTable,
    ParallelFieldOperatorComposer,
)
from .symmetrized_pbw_composition import SymmetrizedPBWComposer


def natural_pbw_adjoint(
    table: Mapping[tuple[int, ...], sp.Matrix],
    pairing: sp.Matrix,
) -> dict[tuple[int, ...], sp.Matrix]:
    """Formal adjoint of a *symmetrized-PBW* parallel operator table.

    The input contract is important: ordered-word coefficients which have
    already absorbed curvature commutators are not parallel coefficient
    tensors and must not be passed here.
    """

    if pairing.shape != (24, 24) or pairing.det() == 0:
        raise ValueError("natural PBW adjoint requires a nondegenerate pairing")
    inverse = pairing.inv()
    return {
        word: sp.Matrix(
            (-1) ** len(word) * inverse * matrix.T * pairing
        ).applyfunc(sp.expand)
        for word, matrix in table.items()
        if matrix != sp.zeros(24)
    }


def _table_defect_count(
    left: Mapping[tuple[int, ...], sp.Matrix],
    right: Mapping[tuple[int, ...], sp.Matrix],
) -> int:
    return sum(
        value != 0
        for word in set(left) | set(right)
        for value in sp.Matrix(
            left.get(word, sp.zeros(24)) - right.get(word, sp.zeros(24))
        ).applyfunc(sp.expand)
    )


def _first_self_adjoint_basis(
    first_basis: sp.Matrix, pairing: sp.Matrix
) -> sp.Matrix:
    """Coordinates of self-adjoint invariant first-order operators.

    A first-order operator is self-adjoint precisely when every parallel
    coefficient obeys ``A^mu+J^-1(A^mu)^T J=0``.
    """

    inverse = pairing.inv()
    columns = []
    for column in range(first_basis.cols):
        values = []
        for coefficient in _coefficient_tuple(first_basis[:, column]):
            defect = coefficient + inverse * coefficient.T * pairing
            values.extend(
                defect[row, col]
                for col in range(24)
                for row in range(24)
            )
        columns.append(sp.SparseMatrix(2304, 1, values))
    constraints = sp.SparseMatrix.hstack(*columns)
    return DomainMatrix.from_Matrix(constraints).nullspace().to_Matrix().T


def _zeroth_self_adjoint_basis(
    zeroth_basis: sp.Matrix, pairing: sp.Matrix
) -> sp.Matrix:
    inverse = pairing.inv()
    columns = []
    for column in range(zeroth_basis.cols):
        coefficient = _endomorphism(zeroth_basis[:, column])
        defect = coefficient - inverse * coefficient.T * pairing
        columns.append(
            sp.SparseMatrix(
                576,
                1,
                [
                    defect[row, col]
                    for col in range(24)
                    for row in range(24)
                ],
            )
        )
    constraints = sp.SparseMatrix.hstack(*columns)
    return DomainMatrix.from_Matrix(constraints).nullspace().to_Matrix().T


def _homogeneous_cubic_words() -> tuple[tuple[int, int, int], ...]:
    return tuple(
        item
        for item in product(range(4), repeat=3)
        if item[0] <= item[1] <= item[2]
    )


def _unisolvent_cubic_points() -> tuple[tuple[tuple[int, ...], ...], int]:
    """Select an exact unisolvent evaluation basis for cubic polynomials."""

    words = _homogeneous_cubic_words()
    points: list[tuple[int, ...]] = []
    rows: list[list[int]] = []
    rank = 0
    for point in product(range(-2, 3), repeat=4):
        if point == (0, 0, 0, 0):
            continue
        row = [point[a] * point[b] * point[c] for a, b, c in words]
        candidate = sp.Matrix(rows + [row])
        new_rank = candidate.rank()
        if new_rank > rank:
            points.append(point)
            rows.append(row)
            rank = new_rank
        if rank == len(words):
            break
    evaluation = sp.Matrix(rows)
    if evaluation.shape != (20, 20) or evaluation.det() == 0:
        raise AssertionError("cubic evaluation points are not unisolvent")
    return tuple(points), int(evaluation.det())


def _cubic_sharp_gate(
    first_basis: sp.Matrix,
    first_self_coordinates: sp.Matrix,
) -> tuple[tuple[int, int], int, int, int, int, int, int]:
    """Solve ``X_1 P_2=q S_L`` by exact unisolvent evaluation."""

    prenormal = AuxiliaryPrenormalSymbol.build()
    points, evaluation_determinant = _unisolvent_cubic_points()
    self_basis = first_basis * first_self_coordinates
    x_coefficients = tuple(
        _coefficient_tuple(self_basis[:, column])
        for column in range(self_basis.cols)
    )
    s_coefficients = tuple(
        _coefficient_tuple(first_basis[:, column])
        for column in range(first_basis.cols)
    )
    entries: dict[tuple[int, int], sp.Expr] = {}
    total_columns = len(x_coefficients) + len(s_coefficients)
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
        for offset, coefficients in enumerate(s_coefficients):
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
    equations = sp.SparseMatrix(20 * 576, total_columns, entries)
    domain = DomainMatrix.from_Matrix(equations)
    rank = domain.rank()
    kernel = domain.nullspace().to_Matrix().T
    x_projection = DomainMatrix.from_Matrix(
        kernel[: self_basis.cols, :]
    ).rank()
    s_projection = DomainMatrix.from_Matrix(
        kernel[self_basis.cols :, :]
    ).rank()
    return (
        equations.shape,
        rank,
        equations.cols - rank,
        x_projection,
        s_projection,
        len(points),
        evaluation_determinant,
    )


@dataclass(frozen=True)
class GeneralAdjointFactorReduction:
    zeroth_invariant_dimension: int
    zeroth_self_adjoint_dimension: int
    first_invariant_dimension: int
    first_self_adjoint_dimension: int
    cubic_evaluation_determinant: int
    cubic_equation_shape: tuple[int, int]
    cubic_rank: int
    cubic_solution_dimension: int
    cubic_x_projection_rank: int
    cubic_sum_projection_rank: int
    factor_split_dimension: int
    left_factor_zeroth_dimension: int
    nonlinear_parameter_dimension: int
    p_adjoint_defect: int
    d_naive_adjoint_defect: int
    product_adjoint_defect: int
    naive_ordered_box_square_defect: int

    @staticmethod
    def build() -> "GeneralAdjointFactorReduction":
        # The exhaustive PBW basis verifier has its own repository
        # certificate.  Here we reuse that exact implementation without
        # retaining its large four-jet audit cache alongside the cubic rank
        # system.
        pbw = SymmetrizedPBWComposer(ParallelFieldOperatorComposer.build())
        pairing = _ordinary_system().field_fibre_pairing

        # Complete the PBW/adjoint audit before the large cubic rank solve and
        # release its fourth-order tables.  Keeping both exact sparse problems
        # resident needlessly multiplies peak memory in constrained runners.
        field, complement, box = _field_operator_tables(pbw)
        field_pbw = pbw.table_to_symmetrized(field)
        complement_pbw = pbw.table_to_symmetrized(complement)
        dp = pbw.compose(complement, field)
        pd = pbw.compose(field, complement)
        p_adjoint_defect = _table_defect_count(
            natural_pbw_adjoint(field_pbw, pairing), field_pbw
        )
        d_adjoint_defect = _table_defect_count(
            natural_pbw_adjoint(complement_pbw, pairing), complement_pbw
        )
        product_adjoint_defect = _table_defect_count(
            natural_pbw_adjoint(dp, pairing), pd
        )
        box_square_ordered = pbw.ordered.compose(box, box)
        naive_ordered = pbw.ordered.naive_sorted_table_adjoint(box_square_ordered)
        naive_defect = _table_defect_count(naive_ordered, box_square_ordered)
        del (
            field,
            complement,
            box,
            field_pbw,
            complement_pbw,
            dp,
            pd,
            box_square_ordered,
            naive_ordered,
            pbw,
        )
        sp.core.cache.clear_cache()
        gc.collect()

        first_invariance = DomainMatrix.from_Matrix(
            _field_first_order_invariance_matrix()
        )
        first_basis = first_invariance.nullspace().to_Matrix().T
        zeroth_basis = _zeroth_invariant_basis()
        first_self = _first_self_adjoint_basis(first_basis, pairing)
        zeroth_self = _zeroth_self_adjoint_basis(zeroth_basis, pairing)
        cubic = _cubic_sharp_gate(first_basis, first_self)
        if cubic[5] != 20:
            raise AssertionError("cubic evaluation ledger drifted")

        result = GeneralAdjointFactorReduction(
            zeroth_invariant_dimension=zeroth_basis.cols,
            zeroth_self_adjoint_dimension=zeroth_self.cols,
            first_invariant_dimension=first_basis.cols,
            first_self_adjoint_dimension=first_self.cols,
            cubic_evaluation_determinant=cubic[6],
            cubic_equation_shape=cubic[0],
            cubic_rank=cubic[1],
            cubic_solution_dimension=cubic[2],
            cubic_x_projection_rank=cubic[3],
            cubic_sum_projection_rank=cubic[4],
            factor_split_dimension=first_basis.cols,
            left_factor_zeroth_dimension=2 * zeroth_basis.cols,
            nonlinear_parameter_dimension=(
                cubic[2] + first_basis.cols + zeroth_self.cols
                + 2 * zeroth_basis.cols
            ),
            p_adjoint_defect=p_adjoint_defect,
            d_naive_adjoint_defect=d_adjoint_defect,
            product_adjoint_defect=product_adjoint_defect,
            naive_ordered_box_square_defect=naive_defect,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if (
            self.zeroth_invariant_dimension,
            self.zeroth_self_adjoint_dimension,
        ) != (38, 24):
            raise AssertionError("zeroth-order sharp dimensions drifted")
        if (
            self.first_invariant_dimension,
            self.first_self_adjoint_dimension,
        ) != (93, 44):
            raise AssertionError("first-order sharp dimensions drifted")
        if self.cubic_evaluation_determinant != 3623878656:
            raise AssertionError("cubic unisolvent determinant drifted")
        if (
            self.cubic_equation_shape,
            self.cubic_rank,
            self.cubic_solution_dimension,
            self.cubic_x_projection_rank,
            self.cubic_sum_projection_rank,
        ) != ((11520, 137), 116, 21, 21, 21):
            raise AssertionError("sharp-reduced cubic solve drifted")
        if (
            self.factor_split_dimension,
            self.left_factor_zeroth_dimension,
            self.nonlinear_parameter_dimension,
        ) != (93, 76, 214):
            raise AssertionError("sharp-reduced nonlinear ledger drifted")
        if (
            self.p_adjoint_defect,
            self.d_naive_adjoint_defect,
            self.product_adjoint_defect,
        ) != (0, 0, 0):
            raise AssertionError("natural PBW adjoint identity failed")
        if self.naive_ordered_box_square_defect != 48:
            raise AssertionError("ordered-word adjoint fail-closed guard drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-general-adjoint-factor-reduction-v1",
            "scope": {
                "pairing": "exact action field pairing J_act",
                "field_operator": "P^sharp=P",
                "complement": "D=D_naive+X_1.nabla+X_0 with D^sharp=D",
                "left_product": "DP=L_- L_+",
                "right_factors": "R_-=L_+^sharp, R_+=L_-^sharp",
                "right_product": "PD=(DP)^sharp=R_- R_+",
                "isotropy": "complete parallel SO(3)-invariant families",
            },
            "pairing_aware_adjoint": {
                "normal_form": "symmetrized covariant-jet/PBW",
                "formula": "(A^I nabla_(I))^sharp=(-1)^|I| J^-1 (A^I)^T J nabla_(I)",
                "P_sharp_minus_P_nonzero_entries": self.p_adjoint_defect,
                "D_naive_sharp_minus_D_naive_nonzero_entries": (
                    self.d_naive_adjoint_defect
                ),
                "sharp_DP_minus_PD_nonzero_entries": self.product_adjoint_defect,
                "naive_ordered_word_box_square_defect": (
                    self.naive_ordered_box_square_defect
                ),
                "naive_ordered_word_transpose_rejected": True,
            },
            "complete_sharp_dimensions": {
                "zeroth_invariant": self.zeroth_invariant_dimension,
                "zeroth_self_adjoint": self.zeroth_self_adjoint_dimension,
                "first_invariant": self.first_invariant_dimension,
                "first_self_adjoint_operator": self.first_self_adjoint_dimension,
            },
            "exact_cubic_gate": {
                "equation": "X_1 P_2=q(A_-+A_+)",
                "polynomial_identity_method": (
                    "evaluation on an exact 20-point unisolvent basis for "
                    "homogeneous cubics in four variables"
                ),
                "evaluation_determinant": self.cubic_evaluation_determinant,
                "matrix_shape": list(self.cubic_equation_shape),
                "rank": self.cubic_rank,
                "solution_dimension": self.cubic_solution_dimension,
                "projection_rank_X1": self.cubic_x_projection_rank,
                "projection_rank_factor_sum": self.cubic_sum_projection_rank,
                "right_cubic_equation_independent": False,
                "reason": "it is the formal adjoint of the left equation",
                "cubic_obstruction": False,
            },
            "remaining_nonlinear_problem": {
                "cubic_family_parameters": self.cubic_solution_dimension,
                "left_first_order_split_parameters": self.factor_split_dimension,
                "self_adjoint_X0_parameters": self.zeroth_self_adjoint_dimension,
                "left_factor_zeroth_parameters": self.left_factor_zeroth_dimension,
                "total_parameters": self.nonlinear_parameter_dimension,
                "remaining_orders": [2, 1, 0],
                "quadratic_products": "A_-^mu A_+^nu",
                "right_equations_need_not_be_solved_separately": True,
                "exact_lower_order_solution_found": False,
                "exact_lower_order_no_go_found": False,
            },
            "outcome": {
                "pairing_aware_adjoint_backend_complete": True,
                "sharp_reduced_cubic_family_dimension": (
                    self.cubic_solution_dimension
                ),
                "general_factorization_proved": False,
                "general_factorization_disproved": False,
                "mixed_order_green_realization": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "The natural action-pairing adjoint removes all independent "
                "right-factor variables and reduces the complete cubic family "
                "to 21 dimensions.  Restoring the left factor split and "
                "algebraic terms leaves an exact 214-parameter nonlinear "
                "orders-2/1/0 solve.  This certificate neither solves nor "
                "obstructs that remaining system."
            ),
        }
