"""Small exact semisimplicity gate for relative pairs (1,7) and (2,7).

The alternative-incidence sensitivity certificate proves that the complete
first-order ``R7sharp`` family acts nontrivially on the old ``h23/f23``
Jordan-obstruction quotient.  Nonzero sensitivity is only a screening
condition, however.  This module therefore assembles the smallest exact
temporally regular coefficient slices in the deterministic equivariant
nullspace bases and tests their aligned matrix polynomials before attempting
any symmetrizer.

For both branches the first temporally regular slice uses two coefficient
basis vectors on each side of the reciprocal saddle:

* pair (1,7): ``R1_0=b0-b3`` and ``R7sharp_0=b2-b17``;
* pair (2,7): ``R2=b0-b3`` and the same ``R7sharp_0``.

The temporal field Schur determinant is eight in either case.  Their aligned
characteristic determinants have only real roots, but exact determinant
valuations exceed kernel dimensions at zero and at both unit-speed roots.
Thus both minimal slices are regular and causal-characteristic, yet not
polynomially semisimple.  A one-parameter spatial ``R7sharp`` direction
whose *direct* chain sensitivity is nonzero also fails to repair either
slice.

This is not a no-go theorem for the complete pair-(1,7) or pair-(2,7)
families.  It is the requested sensitivity-first, semisimplicity-before-
symmetrizer rejection of their smallest exact coefficient slices.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .expanded_relative_witness_commutant import (
    _block_generators,
    _commutant_matrix,
)
from .expanded_relative_witness_full_symbol import (
    COMPLETE_RANK,
    ExpandedRelativeFullSymbol,
    _connected_determinant,
    _symbol_from_quadratic_coefficients,
)
from .expanded_relative_witness_incidence_screen import (
    ALIGNED_EIGENVECTOR_COLUMN,
    ALIGNED_GENERALIZED_COLUMN,
    ExpandedRelativeIncidenceScreen,
    _spatial_variable,
)
from .weyl_cotton_block_green_witness import _constraint_definition_tables
from .weyl_cotton_hyperbolic import ConstraintAdjustedWeylCottonEvolution


FIELD_RANK = 24
CURVATURE_RANK = 92
PAIR17_MULTIPLICITIES = (52, 28, 28, 10, 10, 6, 6)
PAIR27_MULTIPLICITIES = (48, 30, 30, 8, 8, 8, 8)
ROOT_LABELS = (
    "0",
    "+1",
    "-1",
    "+1/2",
    "-1/2",
    "+1/sqrt(3)",
    "-1/sqrt(3)",
)


def _digest(matrix: sp.MatrixBase) -> str:
    sparse = sp.SparseMatrix(matrix)
    payload = [f"{sparse.rows}x{sparse.cols}"]
    payload.extend(
        f"{row},{column}:{sp.srepr(value)}"
        for (row, column), value in sorted(sparse.todok().items())
    )
    return hashlib.sha256("\n".join(payload).encode("utf-8")).hexdigest()


def _reshape_intertwiner(
    vector: sp.MatrixBase, target: int, source: int
) -> sp.Matrix:
    return sp.Matrix(
        target,
        source,
        lambda output, input_: vector[input_ * target + output],
    )


def _first_spatial_table(vector: sp.MatrixBase) -> sp.Matrix:
    return sp.Matrix(
        40,
        24,
        lambda output, input_: vector[
            _spatial_variable(0, output, input_)
        ],
    )


def _root_values() -> tuple[sp.Expr, ...]:
    inverse_sqrt_three = sp.sqrt(sp.Rational(1, 3))
    return (
        sp.Integer(0),
        sp.Integer(1),
        sp.Integer(-1),
        sp.Rational(1, 2),
        sp.Rational(-1, 2),
        inverse_sqrt_three,
        -inverse_sqrt_three,
    )


@dataclass(frozen=True)
class AlternativeSemisimplicityScreen:
    incidence: ExpandedRelativeIncidenceScreen
    r1_temporal_basis: tuple[sp.Matrix, ...]
    r2_algebraic_basis: tuple[sp.Matrix, ...]
    r7_temporal_basis: tuple[sp.Matrix, ...]
    r7_spatial_first_basis: tuple[sp.Matrix, ...]
    selected_r1: sp.Matrix
    selected_r2: sp.Matrix
    selected_r7_temporal: sp.Matrix
    selected_r7_spatial: sp.Matrix
    pair17_temporal_field_schur: sp.Matrix
    pair27_temporal_field_schur: sp.Matrix
    pair17_time_only: sp.Matrix
    pair27_time_only: sp.Matrix
    pair17_spatial_slice: sp.Matrix
    pair27_spatial_slice: sp.Matrix
    pair17_determinant: sp.Expr
    pair27_determinant: sp.Expr
    pair17_nullities: tuple[int, ...]
    pair27_nullities: tuple[int, ...]
    pair17_spatial_nullities: tuple[int, ...]
    pair27_spatial_nullities: tuple[int, ...]

    @staticmethod
    def build() -> "AlternativeSemisimplicityScreen":
        incidence = ExpandedRelativeIncidenceScreen.build()
        generators = _block_generators()
        r1_basis = tuple(
            _reshape_intertwiner(vector, 9, 40)
            for vector in _commutant_matrix(
                generators[0], generators[11]
            ).nullspace()
        )
        r2_basis = tuple(
            _reshape_intertwiner(vector, 9, 26)
            for vector in _commutant_matrix(
                generators[0], generators[15]
            ).nullspace()
        )
        r7_temporal = tuple(
            _reshape_intertwiner(vector, 40, 24)
            for vector in incidence.temporal_basis
        )
        r7_spatial = tuple(
            _first_spatial_table(vector) for vector in incidence.spatial_basis
        )

        selected_r1 = r1_basis[0] - r1_basis[3]
        selected_r2 = r2_basis[0] - r2_basis[3]
        selected_r7_temporal = r7_temporal[2] - r7_temporal[17]
        # Basis direction one is the first exact spatial coordinate whose
        # direct h23/f23 sensitivity is nonzero.
        selected_r7_spatial = r7_spatial[1]

        full = ExpandedRelativeFullSymbol.build()
        adjusted = ConstraintAdjustedWeylCottonEvolution.build()
        constraint = _constraint_definition_tables(adjusted)
        z = sp.Symbol("alternative_relative_z")
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

        temporal_field = _symbol_from_quadratic_coefficients(
            full.paired_hessian_coefficients, (1, 0, 0, 0)
        ) + full.separated_scalar_diagonal
        pair17_schur = (
            temporal_field
            + full.gauge_coefficients[0]
            * selected_r1
            * selected_r7_temporal
        )
        pair27_schur = (
            temporal_field
            + full.gauge_coefficients[0]
            * selected_r2
            * selected_r7_temporal[:26, :]
        )

        def pair17(spatial: sp.Matrix) -> sp.Matrix:
            r1_symbol = -z * selected_r1
            r7_symbol = -z * selected_r7_temporal + spatial
            b = sp.zeros(FIELD_RANK, CURVATURE_RANK)
            b[:, 26:66] = gauge * r1_symbol
            c = sp.zeros(CURVATURE_RANK, FIELD_RANK)
            c[26:66, :] = r7_symbol
            # EcurvSharp=-Ecurv^T for the first-order principal table, so
            # the formal incidence -EcurvSharp R7sharp has the plus sign.
            c[66:92, :] = curvature_equation.T * r7_symbol
            return field.row_join(b).col_join(
                c.row_join(curvature_diagonal)
            )

        def pair27(spatial: sp.Matrix) -> sp.Matrix:
            r7_symbol = -z * selected_r7_temporal + spatial
            b = sp.zeros(FIELD_RANK, CURVATURE_RANK)
            b[:, 66:92] = gauge * selected_r2
            c = sp.zeros(CURVATURE_RANK, FIELD_RANK)
            # The direct X_Eq#<-M row has weighted order one and is absent
            # from this pair-(2,7) order-(0,1) principal polynomial.
            c[66:92, :] = curvature_equation.T * r7_symbol
            return field.row_join(b).col_join(
                c.row_join(curvature_diagonal)
            )

        zero_spatial = sp.zeros(40, 24)
        p17 = pair17(zero_spatial)
        p27 = pair27(zero_spatial)
        p17_spatial = pair17(selected_r7_spatial)
        p27_spatial = pair27(selected_r7_spatial)
        det17 = sp.factor(_connected_determinant(p17))
        det27 = sp.factor(_connected_determinant(p27))
        roots = _root_values()

        def nullities(polynomial: sp.Matrix) -> tuple[int, ...]:
            return tuple(
                COMPLETE_RANK - polynomial.subs(z, root).rank()
                for root in roots
            )

        result = AlternativeSemisimplicityScreen(
            incidence=incidence,
            r1_temporal_basis=r1_basis,
            r2_algebraic_basis=r2_basis,
            r7_temporal_basis=r7_temporal,
            r7_spatial_first_basis=r7_spatial,
            selected_r1=selected_r1,
            selected_r2=selected_r2,
            selected_r7_temporal=selected_r7_temporal,
            selected_r7_spatial=selected_r7_spatial,
            pair17_temporal_field_schur=pair17_schur,
            pair27_temporal_field_schur=pair27_schur,
            pair17_time_only=p17,
            pair27_time_only=p27,
            pair17_spatial_slice=p17_spatial,
            pair27_spatial_slice=p27_spatial,
            pair17_determinant=det17,
            pair27_determinant=det27,
            pair17_nullities=nullities(p17),
            pair27_nullities=nullities(p27),
            pair17_spatial_nullities=nullities(p17_spatial),
            pair27_spatial_nullities=nullities(p27_spatial),
        )
        result.verify()
        return result

    def verify(self) -> None:
        z = sp.Symbol("alternative_relative_z")
        if len(self.r1_temporal_basis) != 18:
            raise AssertionError("R1 temporal family dimension drifted")
        if len(self.r2_algebraic_basis) != 4:
            raise AssertionError("R2 algebraic family dimension drifted")
        if len(self.r7_temporal_basis) != 36:
            raise AssertionError("R7sharp temporal family dimension drifted")
        if len(self.r7_spatial_first_basis) != 86:
            raise AssertionError("R7sharp spatial family dimension drifted")
        if self.pair17_temporal_field_schur.det() != 8:
            raise AssertionError("pair-(1,7) temporal Schur determinant drifted")
        if self.pair27_temporal_field_schur.det() != 8:
            raise AssertionError("pair-(2,7) temporal Schur determinant drifted")

        expected17 = sp.factor(
            z**52
            * (z - 1) ** 28
            * (z + 1) ** 28
            * (2 * z - 1) ** 10
            * (2 * z + 1) ** 10
            * (3 * z**2 - 1) ** 6
            / sp.Integer(95551488)
        )
        expected27 = sp.factor(
            z**48
            * (z - 1) ** 30
            * (z + 1) ** 30
            * (2 * z - 1) ** 8
            * (2 * z + 1) ** 8
            * (3 * z**2 - 1) ** 8
            / sp.Integer(53747712)
        )
        if self.pair17_determinant != expected17:
            raise AssertionError("pair-(1,7) aligned determinant drifted")
        if self.pair27_determinant != expected27:
            raise AssertionError("pair-(2,7) aligned determinant drifted")
        if self.pair17_nullities != (33, 26, 26, 10, 10, 6, 6):
            raise AssertionError("pair-(1,7) nullity ledger drifted")
        if self.pair27_nullities != (29, 28, 28, 8, 8, 8, 8):
            raise AssertionError("pair-(2,7) nullity ledger drifted")
        if self.pair17_spatial_nullities != (33, 26, 26, 8, 8, 6, 6):
            raise AssertionError("pair-(1,7) spatial-slice ledger drifted")
        if self.pair27_spatial_nullities != self.pair27_nullities:
            raise AssertionError("pair-(2,7) spatial-slice ledger drifted")
        direct = self.selected_r7_spatial[:, (
            ALIGNED_EIGENVECTOR_COLUMN,
            ALIGNED_GENERALIZED_COLUMN,
        )]
        if direct == sp.zeros(40, 2) or direct.rank() == 0:
            raise AssertionError("selected R7sharp spatial direction has zero sensitivity")

    def certificate(self) -> dict[str, object]:
        self.verify()

        def root_ledger(
            multiplicities: tuple[int, ...], nullities: tuple[int, ...]
        ) -> list[dict[str, object]]:
            return [
                {
                    "root": label,
                    "determinant_valuation": multiplicity,
                    "kernel_dimension": nullity,
                    "semisimple": multiplicity == nullity,
                    "defect": multiplicity - nullity,
                }
                for label, multiplicity, nullity in zip(
                    ROOT_LABELS, multiplicities, nullities, strict=True
                )
            ]

        return {
            "schema": "pure-weyl-expanded-relative-alternative-semisimplicity-v1",
            "coefficient_basis": {
                "source": "exact nullspaces of actual SO(3) rotation-generator equations",
                "R1_temporal_dimension": len(self.r1_temporal_basis),
                "R2_algebraic_dimension": len(self.r2_algebraic_basis),
                "R7sharp_temporal_dimension": len(self.r7_temporal_basis),
                "R7sharp_spatial_dimension": len(self.r7_spatial_first_basis),
                "pair_1_plus_7_slice": {
                    "R1": "basis[0]-basis[3]",
                    "R7sharp_temporal": "basis[2]-basis[17]",
                    "raw_basis_support": 4,
                },
                "pair_2_plus_7_slice": {
                    "R2": "basis[0]-basis[3]",
                    "R7sharp_temporal": "basis[2]-basis[17]",
                    "raw_basis_support": 4,
                },
                "selected_spatial_perturbation": "R7sharp spatial basis[1]",
                "selected_spatial_direct_sensitivity_rank": self.selected_r7_spatial[
                    :,
                    (
                        ALIGNED_EIGENVECTOR_COLUMN,
                        ALIGNED_GENERALIZED_COLUMN,
                    ),
                ].rank(),
            },
            "temporal_regularity": {
                "pair_1_plus_7_field_Schur_determinant": int(
                    self.pair17_temporal_field_schur.det()
                ),
                "pair_2_plus_7_field_Schur_determinant": int(
                    self.pair27_temporal_field_schur.det()
                ),
                "both_temporal_symbols_invertible": True,
                "pair_1_plus_7_Schur_sha256": _digest(
                    self.pair17_temporal_field_schur
                ),
                "pair_2_plus_7_Schur_sha256": _digest(
                    self.pair27_temporal_field_schur
                ),
            },
            "pair_1_plus_7": {
                "aligned_determinant": str(self.pair17_determinant),
                "all_characteristic_roots_real": True,
                "root_ledger": root_ledger(
                    PAIR17_MULTIPLICITIES, self.pair17_nullities
                ),
                "polynomial_semisimple": False,
                "spatial_basis1_nullities": list(
                    self.pair17_spatial_nullities
                ),
                "spatial_basis1_repairs_semisimplicity": False,
                "polynomial_sha256": _digest(self.pair17_time_only),
            },
            "pair_2_plus_7": {
                "aligned_determinant": str(self.pair27_determinant),
                "all_characteristic_roots_real": True,
                "root_ledger": root_ledger(
                    PAIR27_MULTIPLICITIES, self.pair27_nullities
                ),
                "polynomial_semisimple": False,
                "direct_R7sharp_row_weighted_principal": False,
                "reason": (
                    "for orders (R2,R7sharp)=(0,1), the direct order-one "
                    "X_Eq_sharp<-M row is subprincipal; the leading reciprocal "
                    "row is -EcurvSharp R7sharp of order two"
                ),
                "spatial_basis1_nullities": list(
                    self.pair27_spatial_nullities
                ),
                "spatial_basis1_repairs_semisimplicity": False,
                "polynomial_sha256": _digest(self.pair27_time_only),
            },
            "screening_conclusion": {
                "pair_1_plus_7_minimal_slice_rejected": True,
                "pair_2_plus_7_minimal_slice_rejected": True,
                "rejection_stage": "polynomial semisimplicity",
                "symmetrizer_attempt_warranted": False,
                "complete_pair_1_plus_7_family_ruled_out": False,
                "complete_pair_2_plus_7_family_ruled_out": False,
                "next_if_route_B_continues": (
                    "solve coefficient conditions that increase the zero/unit-root "
                    "kernel dimensions to their determinant valuations before any "
                    "full-family symmetrizer search"
                ),
            },
            "scope": (
                "exact rejection of the displayed smallest temporally regular "
                "coefficient slices and one direct-sensitivity spatial direction; "
                "not a no-go for the complete alternative-incidence families"
            ),
            "strong_hyperbolicity_pair_1_plus_7": False,
            "strong_hyperbolicity_pair_2_plus_7": False,
            "prolonged_green_witness": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
