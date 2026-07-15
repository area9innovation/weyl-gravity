"""Exact four-orientation test for a bare-Box mixed-order factor branch.

The complete cubic gate leaves a 45-dimensional simultaneous family
``(X_1,S_L,S_R)``.  This module asks whether either factor in each of

``D P=L_-L_+`` and ``P D=R_-R_+``

can be the literal rough wave operator.  The other factor is allowed the
complete invariant form ``Box+S^mu nabla_mu+B`` and
``D=D_naive+X_1^mu nabla_mu+X_0`` has the complete invariant algebraic
correction.  Once one factor is bare, every remaining coefficient equation
is linear.  All products are reduced in the exhaustive symmetrized
covariant-jet PBW basis, including cylinder curvature commutators.

This is intentionally a scoped branch test.  An obstruction here says
nothing about the general two-nontrivial-factor family, where the quadratic
term ``A_-^mu A_+^nu`` is available.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping

import sympy as sp
from sympy.polys.matrices import DomainMatrix

from .auxiliary_lower_order_factor_ansatz import (
    _coefficient_tuple,
    _cubic_coefficient_vector,
    _field_first_order_invariance_matrix,
)
from .auxiliary_prenormal_symbol import AuxiliaryPrenormalSymbol
from .conventions import CurvedBVConventions, _ordinary_system
from .expanded_hessian import load_coefficient_cache
from .invariant_pairings import InvariantFibrePairingAnsatz
from .null_symbol_rank_obstruction import DEFAULT_CACHE
from .parallel_operator_composition import (
    OperatorTable,
    _canonicalize_table,
    polynomial_table,
)
from .symmetrized_pbw_composition import SymmetrizedPBWComposer


RowKey = tuple[str, tuple[int, ...], int, int]


def _add_tables(
    *terms: tuple[sp.Expr, OperatorTable],
) -> dict[tuple[int, ...], sp.Matrix]:
    result: dict[tuple[int, ...], sp.Matrix] = defaultdict(lambda: sp.zeros(24))
    for scale, table in terms:
        for word, matrix in table.items():
            result[word] += scale * matrix
    return {
        word: matrix.applyfunc(sp.expand)
        for word, matrix in result.items()
        if matrix.applyfunc(sp.expand) != sp.zeros(24)
    }


def _zeroth_invariant_basis() -> sp.Matrix:
    """Return the complete 38-dimensional parallel endomorphism family."""

    identity = sp.eye(24)
    rows = []
    for generator in InvariantFibrePairingAnsatz.build().field_generators:
        rows.append(
            sp.kronecker_product(identity, generator)
            - sp.kronecker_product(generator.T, identity)
        )
    equations = sp.Matrix.vstack(*rows)
    basis = DomainMatrix.from_Matrix(equations).nullspace().to_Matrix().T
    if basis.shape != (576, 38):
        raise AssertionError("complete invariant zeroth-order basis drifted")
    return basis


def _endomorphism(vector: sp.Matrix) -> sp.Matrix:
    return sp.Matrix(24, 24, lambda row, column: vector[column * 24 + row])


def _simultaneous_cubic_basis() -> tuple[sp.Matrix, sp.Matrix]:
    """Return the 93 first-order basis and 45-dimensional cubic kernel."""

    invariance = DomainMatrix.from_Matrix(_field_first_order_invariance_matrix())
    first_basis = invariance.nullspace().to_Matrix().T
    if first_basis.shape != (2304, 93):
        raise AssertionError("complete invariant first-order basis drifted")

    prenormal = AuxiliaryPrenormalSymbol.build()
    covector = prenormal.covector
    zeta = sp.Matrix(covector)
    principal = prenormal.field_principal_symbol
    q = prenormal.wave_quadratic
    left_columns = []
    right_columns = []
    scalar_columns = []
    for column in range(first_basis.cols):
        coefficients = _coefficient_tuple(first_basis[:, column])
        symbol = sum(
            (zeta[axis] * coefficients[axis] for axis in range(4)),
            sp.zeros(24),
        )
        left_columns.append(
            _cubic_coefficient_vector(symbol * principal, covector)
        )
        right_columns.append(
            _cubic_coefficient_vector(principal * symbol, covector)
        )
        scalar_columns.append(_cubic_coefficient_vector(q * symbol, covector))
    left = sp.SparseMatrix.hstack(*left_columns)
    right = sp.SparseMatrix.hstack(*right_columns)
    scalar = sp.SparseMatrix.hstack(*scalar_columns)
    zero = sp.zeros(left.rows, first_basis.cols)
    equations = sp.Matrix.vstack(
        left.row_join(-scalar).row_join(zero),
        right.row_join(zero).row_join(-scalar),
    )
    kernel = DomainMatrix.from_Matrix(equations).nullspace().to_Matrix().T
    if kernel.shape != (279, 45):
        raise AssertionError("simultaneous cubic kernel drifted")
    return first_basis, kernel


def _first_table(first_basis: sp.Matrix, coordinates: sp.Matrix) -> dict:
    vector = first_basis * coordinates
    coefficients = _coefficient_tuple(vector)
    return {
        (axis,): matrix
        for axis, matrix in enumerate(coefficients)
        if matrix != sp.zeros(24)
    }


def _field_operator_tables(
    pbw: SymmetrizedPBWComposer,
) -> tuple[dict, dict, dict]:
    """Return exact ordered tables ``P,D_naive,Box``."""

    covector, hessian, _ = load_coefficient_cache(DEFAULT_CACHE)
    source = _ordinary_system()
    conventions = CurvedBVConventions.build()
    hessian_table = polynomial_table(
        source.field_fibre_pairing.inv() * hessian,
        covector,
        2,
        normal_form=pbw.normal_form,
    )

    generator = {
        (): conventions.gauge_generator.zeroth_coefficient,
        **{
            (axis,): conventions.gauge_generator.derivative_coefficients[axis]
            for axis in range(4)
        },
    }
    companion = {
        (): conventions.gauge_companion.zeroth_coefficient,
        **{
            (axis,): conventions.gauge_companion.derivative_coefficients[axis]
            for axis in range(4)
        },
    }
    # Rectangular K o C composition.  The resulting table is 24 by 24, and
    # canonicalization acts on the original field input slots exactly as in
    # the square composer.
    gauge_raw: dict[tuple[int, ...], sp.Matrix] = defaultdict(
        lambda: sp.zeros(24)
    )
    for outer_word, outer in generator.items():
        for inner_word, inner in companion.items():
            gauge_raw[outer_word + inner_word] += outer * inner
    gauge_table = _canonicalize_table(gauge_raw, pbw.normal_form)
    field = _add_tables((1, hessian_table), (1, gauge_table))

    metric = source.metric
    box = {
        (axis, axis): metric[axis, axis] * sp.eye(24)
        for axis in range(4)
    }
    complement = _add_tables((2, box), (-1, field))
    return field, complement, box


def _factor_linear_term(
    pbw: SymmetrizedPBWComposer,
    box: OperatorTable,
    coefficient: OperatorTable,
    bare_side: str,
) -> dict:
    if bare_side == "outer":
        return pbw.compose(box, coefficient)
    if bare_side == "inner":
        return pbw.compose(coefficient, box)
    raise ValueError(bare_side)


def _sparse_entries(side: str, table: OperatorTable) -> dict[RowKey, sp.Expr]:
    result = {}
    for word, matrix in table.items():
        for (row, column), value in matrix.todok().items():
            value = sp.expand(value)
            if value != 0:
                result[(side, word, row, column)] = value
    return result


def _matrix_system(
    baseline: Mapping[RowKey, sp.Expr],
    columns: tuple[Mapping[RowKey, sp.Expr], ...],
) -> tuple[tuple[RowKey, ...], sp.SparseMatrix, sp.SparseMatrix]:
    keys = tuple(sorted(set(baseline).union(*(set(column) for column in columns))))
    index = {key: row for row, key in enumerate(keys)}
    entries = {}
    for column_index, column in enumerate(columns):
        for key, value in column.items():
            if value != 0:
                entries[index[key], column_index] = value
    matrix = sp.SparseMatrix(len(keys), len(columns), entries)
    rhs = sp.SparseMatrix(
        len(keys), 1, {(index[key], 0): -value for key, value in baseline.items()}
    )
    return keys, matrix, rhs


def _left_null_witness(
    keys: tuple[RowKey, ...], matrix: sp.Matrix, rhs: sp.Matrix
) -> dict[str, object] | None:
    rank = DomainMatrix.from_Matrix(matrix).rank()
    augmented = matrix.row_join(rhs)
    augmented_rank = DomainMatrix.from_Matrix(augmented).rank()
    if augmented_rank == rank:
        return None

    _, pivots = DomainMatrix.from_Matrix(matrix.T).rref()
    _, augmented_pivots = DomainMatrix.from_Matrix(augmented.T).rref()
    selected = tuple(int(item) for item in pivots)
    extra = next(int(item) for item in augmented_pivots if item not in pivots)
    selected_matrix = matrix[list(selected), :]
    _, pivot_columns = DomainMatrix.from_Matrix(selected_matrix).rref()
    pivot_columns = tuple(int(item) for item in pivot_columns)
    square = selected_matrix[:, list(pivot_columns)]
    target = matrix[extra, list(pivot_columns)]
    coefficients = square.T.inv() * target.T

    witness = sp.zeros(matrix.rows, 1)
    witness[extra] = 1
    for row, coefficient in zip(selected, coefficients, strict=True):
        witness[row] = -coefficient
    if (witness.T * matrix) != sp.zeros(1, matrix.cols):
        raise AssertionError("left-null witness does not annihilate the system")
    pairing = sp.expand((witness.T * rhs)[0])
    if pairing == 0:
        raise AssertionError("left-null witness does not detect inconsistency")

    support = []
    for row, value in witness.todok().items():
        index = row[0]
        side, word, output, input_ = keys[index]
        support.append(
            {
                "equation_row": index,
                "side": side,
                "symmetric_derivative_word": list(word),
                "output_component": output,
                "input_component": input_,
                "coefficient": str(value),
            }
        )
    return {
        "support_size": len(support),
        "support": support,
        "lT_A_is_zero": True,
        "lT_b": str(pairing),
    }


@dataclass(frozen=True)
class TriangularOrientationResult:
    left_bare_side: str
    right_bare_side: str
    equation_shape: tuple[int, int]
    rank: int
    augmented_rank: int
    solution_dimension: int | None
    left_null_witness: dict[str, object] | None

    @property
    def consistent(self) -> bool:
        return self.rank == self.augmented_rank

    def certificate(self) -> dict[str, object]:
        return {
            "left_factorization": (
                "DP=Box o (Box+S_L.nabla+B_L)"
                if self.left_bare_side == "outer"
                else "DP=(Box+S_L.nabla+B_L) o Box"
            ),
            "right_factorization": (
                "PD=Box o (Box+S_R.nabla+B_R)"
                if self.right_bare_side == "outer"
                else "PD=(Box+S_R.nabla+B_R) o Box"
            ),
            "equation_shape": list(self.equation_shape),
            "rank": self.rank,
            "augmented_rank": self.augmented_rank,
            "consistent": self.consistent,
            "solution_dimension": self.solution_dimension,
            "left_null_obstruction": self.left_null_witness,
        }


@dataclass(frozen=True)
class AuxiliaryTriangularBoxFactor:
    cubic_family_dimension: int
    zeroth_invariant_dimension: int
    unknown_count: int
    orientations: tuple[TriangularOrientationResult, ...]

    @staticmethod
    def build() -> "AuxiliaryTriangularBoxFactor":
        pbw = SymmetrizedPBWComposer.build()
        field, complement, box = _field_operator_tables(pbw)
        first_basis, cubic_kernel = _simultaneous_cubic_basis()
        zeroth_basis = _zeroth_invariant_basis()

        box_square = pbw.compose(box, box)
        baseline_left = _add_tables(
            (1, pbw.compose(complement, field)), (-1, box_square)
        )
        baseline_right = _add_tables(
            (1, pbw.compose(field, complement)), (-1, box_square)
        )

        # The first 93 kernel rows are X1, the next 93 S_L, and the final 93 S_R.
        first_triples = []
        for column in range(cubic_kernel.cols):
            first_triples.append(
                tuple(
                    _first_table(
                        first_basis,
                        cubic_kernel[block * 93 : (block + 1) * 93, column],
                    )
                    for block in range(3)
                )
            )
        zeroth_tables = tuple(
            {(): _endomorphism(zeroth_basis[:, column])}
            for column in range(zeroth_basis.cols)
        )

        # Composition is the expensive curvature-aware step.  Cache every
        # orientation-independent product once, then assemble the four exact
        # linear systems by sparse coefficient addition.
        first_products = []
        for x1, s_left, s_right in first_triples:
            first_products.append(
                {
                    "x1_left": pbw.compose(x1, field),
                    "x1_right": pbw.compose(field, x1),
                    "sl_outer": _factor_linear_term(pbw, box, s_left, "outer"),
                    "sl_inner": _factor_linear_term(pbw, box, s_left, "inner"),
                    "sr_outer": _factor_linear_term(pbw, box, s_right, "outer"),
                    "sr_inner": _factor_linear_term(pbw, box, s_right, "inner"),
                }
            )
        zeroth_products = tuple(
            {
                "x0_left": pbw.compose(table, field),
                "x0_right": pbw.compose(field, table),
                "b_outer": _factor_linear_term(pbw, box, table, "outer"),
                "b_inner": _factor_linear_term(pbw, box, table, "inner"),
            }
            for table in zeroth_tables
        )

        results = []
        for left_side in ("outer", "inner"):
            for right_side in ("outer", "inner"):
                columns: list[dict[RowKey, sp.Expr]] = []
                for products in first_products:
                    left = _add_tables(
                        (1, products["x1_left"]),
                        (-1, products[f"sl_{left_side}"]),
                    )
                    right = _add_tables(
                        (1, products["x1_right"]),
                        (-1, products[f"sr_{right_side}"]),
                    )
                    columns.append(
                        {
                            **_sparse_entries("DP", left),
                            **_sparse_entries("PD", right),
                        }
                    )
                # Shared algebraic correction X0.
                for products in zeroth_products:
                    columns.append(
                        {
                            **_sparse_entries("DP", products["x0_left"]),
                            **_sparse_entries("PD", products["x0_right"]),
                        }
                    )
                # Independent algebraic coefficients of the nonbare factors.
                for products in zeroth_products:
                    columns.append(
                        _sparse_entries(
                            "DP",
                            _add_tables((-1, products[f"b_{left_side}"])),
                        )
                    )
                for products in zeroth_products:
                    columns.append(
                        _sparse_entries(
                            "PD",
                            _add_tables((-1, products[f"b_{right_side}"])),
                        )
                    )

                baseline = {
                    **_sparse_entries("DP", baseline_left),
                    **_sparse_entries("PD", baseline_right),
                }
                keys, matrix, rhs = _matrix_system(baseline, tuple(columns))
                rank = DomainMatrix.from_Matrix(matrix).rank()
                augmented_rank = DomainMatrix.from_Matrix(
                    matrix.row_join(rhs)
                ).rank()
                witness = _left_null_witness(keys, matrix, rhs)
                results.append(
                    TriangularOrientationResult(
                        left_bare_side=left_side,
                        right_bare_side=right_side,
                        equation_shape=matrix.shape,
                        rank=rank,
                        augmented_rank=augmented_rank,
                        solution_dimension=(
                            matrix.cols - rank if rank == augmented_rank else None
                        ),
                        left_null_witness=witness,
                    )
                )

        result = AuxiliaryTriangularBoxFactor(
            cubic_family_dimension=cubic_kernel.cols,
            zeroth_invariant_dimension=zeroth_basis.cols,
            unknown_count=45 + 3 * 38,
            orientations=tuple(results),
        )
        result.verify()
        return result

    def verify(self) -> None:
        if (self.cubic_family_dimension, self.zeroth_invariant_dimension) != (45, 38):
            raise AssertionError("triangular factor parameter ledger drifted")
        if self.unknown_count != 159:
            raise AssertionError("triangular factor unknown count drifted")
        if len(self.orientations) != 4:
            raise AssertionError("not all four bare-Box orientations were tested")
        if {
            (item.left_bare_side, item.right_bare_side)
            for item in self.orientations
        } != {(a, b) for a in ("outer", "inner") for b in ("outer", "inner")}:
            raise AssertionError("bare-Box orientation coverage drifted")
        expected_shapes = {
            ("outer", "outer"): (2553, 159),
            ("outer", "inner"): (2547, 159),
            ("inner", "outer"): (2541, 159),
            ("inner", "inner"): (2535, 159),
        }
        for item in self.orientations:
            if item.equation_shape != expected_shapes[
                (item.left_bare_side, item.right_bare_side)
            ]:
                raise AssertionError("triangular factor equation ledger drifted")
            if (item.rank, item.augmented_rank) != (159, 160):
                raise AssertionError("triangular factor rank obstruction drifted")
            if item.consistent != (item.left_null_witness is None):
                raise AssertionError("triangular obstruction witness ledger drifted")
            witness = item.left_null_witness
            if witness is None or witness["support_size"] != 1:
                raise AssertionError("triangular one-row witness drifted")
            support = witness["support"][0]
            if (
                witness["lT_b"],
                support["side"],
                support["symmetric_derivative_word"],
                support["output_component"],
                support["input_component"],
            ) != ("-8", "DP", [0, 1], 10, 11):
                raise AssertionError("triangular obstruction channel drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        consistent = [item for item in self.orientations if item.consistent]
        return {
            "schema": "pure-weyl-auxiliary-triangular-bare-box-factor-v1",
            "ansatz": {
                "complement": "D=D_naive+X_1^mu nabla_mu+X_0",
                "simultaneous_cubic_family_dimension": self.cubic_family_dimension,
                "invariant_algebraic_dimension": self.zeroth_invariant_dimension,
                "unknowns": {
                    "cubic_X1_SL_SR_family": 45,
                    "X0": 38,
                    "B_L": 38,
                    "B_R": 38,
                    "total": self.unknown_count,
                },
                "bare_factor": "exact rough Box with no first- or zeroth-order term",
                "bundle_order": "h[0:10]+f[10:20]+v[20:24]",
                "orientation_count": 4,
                "symmetrized_PBW_curvature_exact": True,
                "parallel_globalization": True,
            },
            "orientations": [item.certificate() for item in self.orientations],
            "outcome": {
                "consistent_orientation_count": len(consistent),
                "all_four_orientations_obstructed": not consistent,
                "common_obstruction_channel": (
                    "the DP coefficient of nabla_(0 nabla_1) mapping f_01 to "
                    "f_00 is -8 in the required right-hand side and zero in "
                    "all 159 correction columns"
                ),
                "general_two_nontrivial_factor_branch_decided": False,
                "mixed_order_factorization_proved": False,
                "green_realization_proved": False,
                "flag_promoted": False,
            },
            "theorem_boundary": (
                "This exact linear solve exhausts only the branch in which one "
                "factor of DP and one factor of PD is the literal rough Box.  "
                "It does not constrain the complete branch with nonzero "
                "first-order coefficients in both factors, whose A_- A_+ term "
                "changes the quadratic equations."
            ),
        }
