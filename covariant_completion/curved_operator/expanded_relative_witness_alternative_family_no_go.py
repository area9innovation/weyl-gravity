"""Exact semisimplicity no-go on the minimal alternative-incidence family.

The complete ``R7sharp`` coefficient family has a 16-dimensional image on
the aligned polynomial-Jordan obstruction: eight temporal and eight spatial
directions.  It is wasteful (and obscures the invariant content) to search
all 122 raw nullspace coefficients.  This module selects the unique
deterministic pivot columns of the exact sensitivity matrix.  The resulting
16-parameter affine family is the smallest temporal-plus-spatial family that
surjects onto that obstruction image.

Both remaining reciprocal incidences nevertheless fail the polynomial
semisimplicity gate uniformly on this family.  The proof uses the zero-speed
root and does not rely on sampling:

* for pair ``(1,7)`` the exact determinant is divisible by ``z**40``, while
  its lower-triangular value at ``z=0`` has nullity at most 33;
* for pair ``(2,7)`` the determinant is parameter independent and divisible
  by ``z**48``, while a parameter-independent 90-row submatrix has rank 69,
  so the full nullity is at most 47.

Thus every regular member is non-semisimple.  A symmetrizer search is not
warranted.  This is deliberately *not* a no-go for either complete
122-parameter incidence family, nor for the generalized triangular Green
route: it closes only the smallest exact family spanning the known
16-dimensional obstruction sensitivity.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .expanded_relative_witness_alternative_semisimplicity import (
    AlternativeSemisimplicityScreen,
)
from .expanded_relative_witness_full_symbol import (
    CURVATURE_RANK,
    FIELD_RANK,
    ExpandedRelativeFullSymbol,
    _connected_determinant,
    _symbol_from_quadratic_coefficients,
)
from .weyl_cotton_block_green_witness import _constraint_definition_tables
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


TEMPORAL_PIVOTS = (8, 9, 10, 11, 22, 23, 24, 25)
SPATIAL_PIVOTS = (1, 3, 6, 8, 11, 13, 16, 18)
PARAMETER_COUNT = 16
COMPLETE_RANK = FIELD_RANK + CURVATURE_RANK


def _digest(matrix: sp.MatrixBase) -> str:
    sparse = sp.SparseMatrix(matrix)
    payload = [f"{sparse.rows}x{sparse.cols}"]
    payload.extend(
        f"{row},{column}:{sp.srepr(value)}"
        for (row, column), value in sorted(sparse.todok().items())
    )
    return hashlib.sha256("\n".join(payload).encode("utf-8")).hexdigest()


def _expression_digest(expression: sp.Expr) -> str:
    return hashlib.sha256(sp.srepr(expression).encode("utf-8")).hexdigest()


def _z_valuation(expression: sp.Expr, z: sp.Symbol) -> int:
    polynomial = sp.Poly(expression, z)
    return min(monomial[0] for monomial, coefficient in polynomial.terms() if coefficient)


def _entry_valuation(expression: sp.Expr, z: sp.Symbol, infinity: int) -> int:
    if expression == 0:
        return infinity
    return _z_valuation(expression, z)


def _tropical_determinant_certificate(
    matrix: sp.MatrixBase, z: sp.Symbol
) -> tuple[int, tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    """Return an exact Hungarian primal/dual certificate.

    Every determinant monomial has ``z``-valuation at least the minimum-cost
    perfect matching of the entry valuations.  Parameter specialization can
    cancel leading coefficients, but can only increase this bound.
    """

    if matrix.rows != matrix.cols:
        raise ValueError("tropical determinant requires a square matrix")
    size = matrix.rows
    infinity = 10**6
    costs = [
        [_entry_valuation(matrix[row, column], z, infinity) for column in range(size)]
        for row in range(size)
    ]
    # Exact integer Hungarian algorithm, with row potentials u and column
    # potentials v satisfying u_i+v_j <= cost_ij.
    u = [0] * (size + 1)
    v = [0] * (size + 1)
    p = [0] * (size + 1)
    way = [0] * (size + 1)
    for row in range(1, size + 1):
        p[0] = row
        column0 = 0
        minv = [infinity] * (size + 1)
        used = [False] * (size + 1)
        while True:
            used[column0] = True
            row0 = p[column0]
            delta = infinity
            column1 = 0
            for column in range(1, size + 1):
                if used[column]:
                    continue
                current = costs[row0 - 1][column - 1] - u[row0] - v[column]
                if current < minv[column]:
                    minv[column] = current
                    way[column] = column0
                if minv[column] < delta:
                    delta = minv[column]
                    column1 = column
            if delta >= infinity:
                raise AssertionError("symbol support has no perfect matching")
            for column in range(size + 1):
                if used[column]:
                    u[p[column]] += delta
                    v[column] -= delta
                else:
                    minv[column] -= delta
            column0 = column1
            if p[column0] == 0:
                break
        while True:
            column1 = way[column0]
            p[column0] = p[column1]
            column0 = column1
            if column0 == 0:
                break
    assignment = [-1] * size
    for column in range(1, size + 1):
        assignment[p[column] - 1] = column - 1
    value = sum(costs[row][assignment[row]] for row in range(size))
    row_dual = tuple(u[1:])
    column_dual = tuple(v[1:])
    if value != sum(row_dual) + sum(column_dual):
        raise AssertionError("Hungarian primal/dual objectives disagree")
    for row in range(size):
        for column in range(size):
            if row_dual[row] + column_dual[column] > costs[row][column]:
                raise AssertionError("Hungarian dual is infeasible")
        if costs[row][assignment[row]] >= infinity:
            raise AssertionError("matching uses a structurally zero entry")
        if row_dual[row] + column_dual[assignment[row]] != costs[row][assignment[row]]:
            raise AssertionError("matching edge is not dual tight")
    return value, tuple(assignment), row_dual, column_dual


@dataclass(frozen=True)
class AlternativeFamilyNoGo:
    base: AlternativeSemisimplicityScreen
    z: sp.Symbol
    temporal_parameters: tuple[sp.Symbol, ...]
    spatial_parameters: tuple[sp.Symbol, ...]
    selected_sensitivity: sp.Matrix
    pair17_polynomial: sp.Matrix
    pair27_polynomial: sp.Matrix
    pair17_determinant: sp.Expr
    pair27_determinant: sp.Expr
    pair17_zero_diagonal_ranks: tuple[int, int]
    pair27_fixed_row_rank: int
    pair17_zero_valuation: int
    pair27_zero_valuation: int
    pair17_tropical_matching: tuple[int, ...]
    pair17_tropical_row_dual: tuple[int, ...]
    pair17_tropical_column_dual: tuple[int, ...]
    pair27_tropical_matching: tuple[int, ...]
    pair27_tropical_row_dual: tuple[int, ...]
    pair27_tropical_column_dual: tuple[int, ...]

    @staticmethod
    def build() -> "AlternativeFamilyNoGo":
        base = AlternativeSemisimplicityScreen.build()
        z = sp.Symbol("alternative_family_z")
        # Short generator names materially reduce exact multivariate
        # fraction arithmetic in DomainMatrix without changing the result.
        temporal_parameters = sp.symbols("t0:8")
        spatial_parameters = sp.symbols("x0:8")

        sensitivity_columns = TEMPORAL_PIVOTS + tuple(
            len(base.r7_temporal_basis) + index for index in SPATIAL_PIVOTS
        )
        selected_sensitivity = base.incidence.joint_sensitivity[:, sensitivity_columns]

        temporal = base.selected_r7_temporal + sum(
            (
                parameter * base.r7_temporal_basis[index]
                for parameter, index in zip(
                    temporal_parameters, TEMPORAL_PIVOTS, strict=True
                )
            ),
            sp.zeros(40, FIELD_RANK),
        )
        spatial = sum(
            (
                parameter * base.r7_spatial_first_basis[index]
                for parameter, index in zip(
                    spatial_parameters, SPATIAL_PIVOTS, strict=True
                )
            ),
            sp.zeros(40, FIELD_RANK),
        )

        full = ExpandedRelativeFullSymbol.build()
        adjusted = ConstraintAdjustedWeylCottonEvolution.build()
        constraint = _constraint_definition_tables(adjusted)
        values = (-z, 1, 0, 0)
        field = _symbol_from_quadratic_coefficients(
            full.paired_hessian_coefficients, values
        ) + z**2 * full.separated_scalar_diagonal
        gauge = -z * full.gauge_coefficients[0] + full.gauge_coefficients[1]
        evolution = (
            -z * full.evolution_coefficients[0]
            + full.evolution_coefficients[1]
        )
        subsidiary = (
            -z * full.subsidiary_coefficients[0]
            + full.subsidiary_coefficients[1]
        )
        curvature_equation = evolution.col_join(constraint[1])
        curvature_diagonal = sp.diag(
            evolution,
            -evolution.T,
            -subsidiary.T,
            -evolution.T,
        )
        r7_symbol = -z * temporal + spatial

        b17 = sp.zeros(FIELD_RANK, CURVATURE_RANK)
        b17[:, 26:66] = gauge * (-z * base.selected_r1)
        c17 = sp.zeros(CURVATURE_RANK, FIELD_RANK)
        c17[26:66, :] = r7_symbol
        c17[66:92, :] = curvature_equation.T * r7_symbol
        pair17 = field.row_join(b17).col_join(
            c17.row_join(curvature_diagonal)
        )

        b27 = sp.zeros(FIELD_RANK, CURVATURE_RANK)
        b27[:, 66:92] = gauge * base.selected_r2
        c27 = sp.zeros(CURVATURE_RANK, FIELD_RANK)
        c27[66:92, :] = curvature_equation.T * r7_symbol
        pair27 = field.row_join(b27).col_join(
            c27.row_join(curvature_diagonal)
        )

        determinant17 = sp.factor(_connected_determinant(pair17))
        determinant27 = sp.factor(_connected_determinant(pair27))
        tropical17 = _tropical_determinant_certificate(pair17, z)
        tropical27 = _tropical_determinant_certificate(pair27, z)

        field_zero = field.subs(z, 0)
        curvature_zero = curvature_diagonal.subs(z, 0)
        # R7sharp enters pair (2,7) only in global rows 90:116.  The first
        # ninety rows are therefore a parameter-independent rank witness.
        pair27_fixed_rows = pair27.subs(z, 0)[:90, :]

        result = AlternativeFamilyNoGo(
            base=base,
            z=z,
            temporal_parameters=temporal_parameters,
            spatial_parameters=spatial_parameters,
            selected_sensitivity=selected_sensitivity,
            pair17_polynomial=pair17,
            pair27_polynomial=pair27,
            pair17_determinant=determinant17,
            pair27_determinant=determinant27,
            pair17_zero_diagonal_ranks=(field_zero.rank(), curvature_zero.rank()),
            pair27_fixed_row_rank=pair27_fixed_rows.rank(),
            pair17_zero_valuation=_z_valuation(determinant17, z),
            pair27_zero_valuation=_z_valuation(determinant27, z),
            pair17_tropical_matching=tropical17[1],
            pair17_tropical_row_dual=tropical17[2],
            pair17_tropical_column_dual=tropical17[3],
            pair27_tropical_matching=tropical27[1],
            pair27_tropical_row_dual=tropical27[2],
            pair27_tropical_column_dual=tropical27[3],
        )
        result.verify()
        return result

    def verify(self) -> None:
        z = self.z
        t = self.temporal_parameters
        x = self.spatial_parameters
        if self.selected_sensitivity.shape != (80, PARAMETER_COUNT):
            raise AssertionError("minimal sensitivity slice shape drifted")
        if self.selected_sensitivity.rank() != PARAMETER_COUNT:
            raise AssertionError("minimal sensitivity slice stopped spanning the image")
        if self.base.incidence.joint_sensitivity.rank() != PARAMETER_COUNT:
            raise AssertionError("complete sensitivity-image dimension drifted")
        if self.pair17_zero_diagonal_ranks != (15, 68):
            raise AssertionError("pair-(1,7) zero-root diagonal ranks drifted")
        if self.pair17_polynomial[:FIELD_RANK, FIELD_RANK:].subs(z, 0) != sp.zeros(
            FIELD_RANK, CURVATURE_RANK
        ):
            raise AssertionError("pair-(1,7) zero-root upper-right block is nonzero")
        if self.pair27_fixed_row_rank != 69:
            raise AssertionError("pair-(2,7) fixed-row rank witness drifted")
        pair27_fixed_rows = self.pair27_polynomial.subs(z, 0)[:90, :]
        if any(
            pair27_fixed_rows.diff(parameter) != sp.zeros(90, COMPLETE_RANK)
            for parameter in (*t, *x)
        ):
            raise AssertionError("pair-(2,7) rank-witness rows depend on parameters")

        expected27 = sp.factor(
            z**48
            * (z - 1) ** 30
            * (z + 1) ** 30
            * (2 * z - 1) ** 8
            * (2 * z + 1) ** 8
            * (3 * z**2 - 1) ** 8
            / sp.Integer(53747712)
        )
        if self.pair27_determinant != expected27:
            raise AssertionError("pair-(2,7) parameter-independent determinant drifted")
        if any(
            sp.diff(self.pair27_determinant, parameter) != 0
            for parameter in (*t, *x)
        ):
            raise AssertionError("pair-(2,7) determinant acquired parameter dependence")
        if self.pair17_zero_valuation != 40:
            raise AssertionError("pair-(1,7) universal zero factor drifted")
        if self.pair27_zero_valuation != 48:
            raise AssertionError("pair-(2,7) universal zero factor drifted")

        coefficient17 = sp.factor(
            sp.Poly(self.pair17_determinant, z).coeff_monomial(z**40)
        )
        expected_coefficient17 = sp.factor(
            (t[3] * t[6] - t[2] * t[7])
            * (x[4] * x[7] - x[5] * x[6]) ** 2
            / sp.Integer(13759414272)
        )
        if coefficient17 != expected_coefficient17:
            raise AssertionError("pair-(1,7) leading zero-root coefficient drifted")

        # At z=0 pair (1,7) has B=0.  Hence [[A,0],[C,D]] has
        # rank at least rank(A)+rank(D)=83 for every C, independently of all
        # spatial parameters.  Pair (2,7) uses the fixed 90-row witness.
        if COMPLETE_RANK - sum(self.pair17_zero_diagonal_ranks) != 33:
            raise AssertionError("pair-(1,7) uniform nullity bound drifted")
        if COMPLETE_RANK - self.pair27_fixed_row_rank != 47:
            raise AssertionError("pair-(2,7) uniform nullity bound drifted")
        if not (
            self.pair17_zero_valuation > 33
            and self.pair27_zero_valuation > 47
        ):
            raise AssertionError("zero-root semisimplicity obstruction disappeared")

    def certificate(self) -> dict[str, object]:
        self.verify()
        z = self.z
        t = self.temporal_parameters
        x = self.spatial_parameters
        coefficient17 = sp.factor(
            sp.Poly(self.pair17_determinant, z).coeff_monomial(z**40)
        )
        active = [
            str(parameter)
            for parameter in (*t, *x)
            if sp.diff(self.pair17_determinant, parameter) != 0
        ]
        return {
            "schema": "pure-weyl-expanded-relative-alternative-family-no-go-v1",
            "minimal_sensitivity_surjection": {
                "complete_raw_parameter_count": 122,
                "complete_sensitivity_image_dimension": 16,
                "selected_parameter_count": PARAMETER_COUNT,
                "temporal_pivot_columns": list(TEMPORAL_PIVOTS),
                "spatial_pivot_columns": list(SPATIAL_PIVOTS),
                "selected_matrix_shape": list(self.selected_sensitivity.shape),
                "selected_matrix_rank": self.selected_sensitivity.rank(),
                "selected_matrix_sha256": _digest(self.selected_sensitivity),
                "minimal_by_rank": True,
                "contains_temporal_and_spatial_directions": True,
            },
            "pair_1_plus_7": {
                "determinant_sha256": _expression_digest(self.pair17_determinant),
                "determinant_active_parameters": active,
                "universal_zero_root_valuation": self.pair17_zero_valuation,
                "leading_z40_coefficient": str(coefficient17),
                "valuation_proof": "exact multivariate DomainMatrix determinant",
                "matching_sha256": _digest(sp.Matrix(self.pair17_tropical_matching)),
                "row_dual_sha256": _digest(sp.Matrix(self.pair17_tropical_row_dual)),
                "column_dual_sha256": _digest(sp.Matrix(self.pair17_tropical_column_dual)),
                "tropical_primal_dual_objective": sum(
                    _entry_valuation(
                        self.pair17_polynomial[row, self.pair17_tropical_matching[row]],
                        z,
                        10**6,
                    )
                    for row in range(COMPLETE_RANK)
                ),
                "zero_root_block_form": "[[A,0],[C(theta),D]]",
                "rank_A": self.pair17_zero_diagonal_ranks[0],
                "rank_D": self.pair17_zero_diagonal_ranks[1],
                "uniform_rank_lower_bound": sum(self.pair17_zero_diagonal_ranks),
                "uniform_kernel_upper_bound": 33,
                "regular_specializations_semisimple_at_zero": False,
                "defect_lower_bound": self.pair17_zero_valuation - 33,
            },
            "pair_2_plus_7": {
                "determinant": str(self.pair27_determinant),
                "determinant_sha256": _expression_digest(self.pair27_determinant),
                "determinant_parameter_independent": True,
                "universal_zero_root_valuation": self.pair27_zero_valuation,
                "tropical_matching_sha256": _digest(sp.Matrix(self.pair27_tropical_matching)),
                "tropical_primal_dual_objective": sum(
                    _entry_valuation(
                        self.pair27_polynomial[row, self.pair27_tropical_matching[row]],
                        z,
                        10**6,
                    )
                    for row in range(COMPLETE_RANK)
                ),
                "parameter_independent_row_range": "0:90",
                "fixed_row_rank": self.pair27_fixed_row_rank,
                "uniform_kernel_upper_bound": 47,
                "semisimple_at_zero": False,
                "defect_lower_bound": self.pair27_zero_valuation - 47,
            },
            "screening_conclusion": {
                "pair_1_plus_7_minimal_spanning_family_semisimple": False,
                "pair_2_plus_7_minimal_spanning_family_semisimple": False,
                "parameter_uniform_zero_root_obstruction": True,
                "symmetrizer_attempt_warranted": False,
                "complete_pair_1_plus_7_family_ruled_out": False,
                "complete_pair_2_plus_7_family_ruled_out": False,
                "generalized_green_extension_ruled_out": False,
            },
            "scope": (
                "exact no-go for the deterministic 16-parameter temporal-plus-"
                "spatial subfamily minimally spanning the complete known Jordan-"
                "sensitivity image; not a no-go for either raw 122-parameter family"
            ),
            "strong_hyperbolicity_on_minimal_pair_1_plus_7_family": False,
            "strong_hyperbolicity_on_minimal_pair_2_plus_7_family": False,
            "prolonged_green_witness": False,
            "warranted_atomic_flags": [
                "alternative_minimal_sensitivity_family_complete",
                "alternative_minimal_family_zero_root_no_go",
            ],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
