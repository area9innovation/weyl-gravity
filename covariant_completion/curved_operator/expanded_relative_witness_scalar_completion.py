"""Exact temporal scalar completion for the expanded relative witness.

The complete invariant incidence audit leaves three central rotation scalars.
This module identifies them in the exact action-normalized auxiliary symbol
and gives a minimal support-local completion of the pair-(1,6) saddle.

At ``zeta=dt`` the paired Hessian has scalar kernel
``span(h_00,f_00,v_0)``.  The scalar restriction of the existing local gauge
completion ``K_1 C_1`` is a rank-three triangular isomorphism on precisely
that kernel.  Explicit pair-(1,6) coefficients also give the local numerator
``K R1 NcurvSharp R6sharp=Pi_vector``.  This is not the saddle Schur term
``B D^{-1} C``: the actual curvature temporal diagonal and its Douglis
inverse have not been inserted.  No saddle-rank, characteristic or
symmetrizer claim is made here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .conventions import SYMMETRIC_COORDINATES, CurvedBVConventions, _ordinary_system
from .expanded_hessian import load_coefficient_cache
from .null_symbol_rank_obstruction import DEFAULT_CACHE
from covariant_completion.curved_retract.curvature_identity_chain_map import (
    CurvatureAuxiliaryIdentityChainMap,
)


SCALAR_BASIS_NAMES = ("h_00", "tr_spatial_h", "f_00", "tr_spatial_f", "v_0")
GAUGE_SCALAR_NAMES = ("h_00", "f_00", "v_0")
VECTOR_GHOST_COLUMNS = (1, 2, 3, 5, 6, 7)


def _integer_matrix(matrix: sp.MatrixBase) -> list[list[int]]:
    return [[int(matrix[row, column]) for column in range(matrix.cols)] for row in range(matrix.rows)]


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _homogeneous_temporal(matrix: sp.MatrixBase, covector: tuple[sp.Symbol, ...]) -> sp.Matrix:
    scale = sp.Symbol("expanded_relative_temporal_scale")
    substitutions = {
        covector[0]: scale,
        covector[1]: 0,
        covector[2]: 0,
        covector[3]: 0,
    }
    return sp.Matrix(matrix).applyfunc(
        lambda value: sp.expand(value.subs(substitutions)).coeff(scale, 2)
    )


def _scalar_embedding() -> sp.Matrix:
    coordinate = {pair: index for index, pair in enumerate(SYMMETRIC_COORDINATES)}
    columns: list[sp.Matrix] = []
    for offset in (0, 10):
        time = sp.zeros(24, 1)
        time[offset + coordinate[(0, 0)]] = 1
        columns.append(time)
        trace = sp.zeros(24, 1)
        for axis in (1, 2, 3):
            trace[offset + coordinate[(axis, axis)]] = 1
        columns.append(trace)
    vector_time = sp.zeros(24, 1)
    vector_time[20] = 1
    columns.append(vector_time)
    return sp.Matrix.hstack(*columns)


@dataclass(frozen=True)
class ExpandedRelativeScalarCompletion:
    paired_hessian_temporal: sp.Matrix
    gauge_completion_temporal: sp.Matrix
    scalar_embedding: sp.Matrix
    scalar_hessian: sp.Matrix
    scalar_gauge_completion: sp.Matrix
    gauge_scalar_embedding: sp.Matrix
    gauge_scalar_diagonal: sp.Matrix
    gauge_generator_temporal: sp.Matrix
    vector_gauge_embedding: sp.Matrix
    vector_gauge_left_inverse: sp.Matrix
    vector_gauge_projector: sp.Matrix
    curvature_identity_temporal: sp.Matrix
    curvature_identity_sharp_temporal: sp.Matrix
    ghost_vector_embedding: sp.Matrix
    identity_vector_embedding: sp.Matrix
    equation_vector_embedding: sp.Matrix
    relative_r1_temporal: sp.Matrix
    relative_r6_sharp_temporal: sp.Matrix
    relative_pair16_product: sp.Matrix
    algebraic_target_complement: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeScalarCompletion":
        covector, hessian, _ = load_coefficient_cache(DEFAULT_CACHE)
        source = _ordinary_system()
        conventions = CurvedBVConventions.build()
        paired_hessian = _homogeneous_temporal(
            source.field_fibre_pairing.inv() * hessian, covector
        )
        generator = conventions.gauge_generator.derivative_coefficients[0]
        companion = conventions.gauge_companion.derivative_coefficients[0]
        gauge_completion = generator * companion

        scalar = _scalar_embedding()
        scalar_left_inverse = (scalar.T * scalar).inv() * scalar.T
        scalar_hessian = scalar_left_inverse * paired_hessian * scalar
        scalar_gauge = scalar_left_inverse * gauge_completion * scalar

        # The first, third and fifth scalar basis vectors are h00,f00,v0.
        gauge_scalar = scalar[:, (0, 2, 4)]
        restricted = gauge_scalar.T * gauge_completion * gauge_scalar
        scalar_diagonal = gauge_scalar * restricted * gauge_scalar.T

        vector_gauge = generator[:, VECTOR_GHOST_COLUMNS]
        vector_left_inverse = (vector_gauge.T * vector_gauge).inv() * vector_gauge.T
        vector_projector = vector_gauge * vector_left_inverse

        # Use the certified temporal curvature identity row N=(0,I_14), not
        # an abstract incidence replacement.  Its cotangent coefficient is
        # the coordinate-dual transpose in the mapping-cylinder pairing.
        identity_chain = CurvatureAuxiliaryIdentityChainMap.build()
        curvature_identity = identity_chain.curvature_identity_coefficients[0]
        curvature_identity_sharp = curvature_identity.T
        ghost_vector = sp.zeros(9, 6)
        for column, row in enumerate(VECTOR_GHOST_COLUMNS):
            ghost_vector[row, column] = 1
        identity_vector = sp.zeros(14, 6)
        identity_vector[:6, :] = sp.eye(6)  # q[3] plus r[3]
        equation_vector = curvature_identity_sharp * identity_vector
        relative_r1 = ghost_vector * equation_vector.T
        relative_r6_sharp = identity_vector * vector_left_inverse
        relative_product = (
            generator
            * relative_r1
            * curvature_identity_sharp
            * relative_r6_sharp
        )
        completed = paired_hessian + scalar_diagonal - relative_product

        result = ExpandedRelativeScalarCompletion(
            paired_hessian_temporal=paired_hessian,
            gauge_completion_temporal=gauge_completion,
            scalar_embedding=scalar,
            scalar_hessian=scalar_hessian,
            scalar_gauge_completion=scalar_gauge,
            gauge_scalar_embedding=gauge_scalar,
            gauge_scalar_diagonal=scalar_diagonal,
            gauge_generator_temporal=generator,
            vector_gauge_embedding=vector_gauge,
            vector_gauge_left_inverse=vector_left_inverse,
            vector_gauge_projector=vector_projector,
            curvature_identity_temporal=curvature_identity,
            curvature_identity_sharp_temporal=curvature_identity_sharp,
            ghost_vector_embedding=ghost_vector,
            identity_vector_embedding=identity_vector,
            equation_vector_embedding=equation_vector,
            relative_r1_temporal=relative_r1,
            relative_r6_sharp_temporal=relative_r6_sharp,
            relative_pair16_product=relative_product,
            algebraic_target_complement=completed,
        )
        result.verify()
        return result

    def verify(self) -> None:
        expected_hessian = sp.Matrix(
            [
                [0, 3, 0, 0, 0],
                [0, -1, 0, 0, 0],
                [0, 0, 0, 3, 0],
                [0, 0, 0, -1, 0],
                [0, 0, 0, 0, 0],
            ]
        )
        if self.scalar_hessian != expected_hessian:
            raise AssertionError("exact temporal scalar Hessian drifted")
        if self.scalar_hessian.rank() != 2:
            raise AssertionError("scalar Hessian rank drifted")
        if self.paired_hessian_temporal * self.gauge_scalar_embedding != sp.zeros(24, 3):
            raise AssertionError("h00,f00,v0 are not the Hessian scalar kernel")
        restricted = (
            self.gauge_scalar_embedding.T
            * self.gauge_completion_temporal
            * self.gauge_scalar_embedding
        )
        expected_restricted = sp.Matrix([[-1, 0, 0], [-4, -1, 0], [0, 0, -1]])
        if restricted != expected_restricted or restricted.det() != -1:
            raise AssertionError("minimal gauge-scalar diagonal is not invertible")
        if self.gauge_scalar_diagonal.rank() != 3:
            raise AssertionError("scalar completion is not minimal rank three")
        if self.vector_gauge_embedding.rank() != 6:
            raise AssertionError("vector gauge image rank drifted")
        if self.paired_hessian_temporal * self.vector_gauge_embedding != sp.zeros(24, 6):
            raise AssertionError("vector gauge image left the Hessian kernel")
        if self.vector_gauge_left_inverse * self.vector_gauge_embedding != sp.eye(6):
            raise AssertionError("explicit vector gauge left inverse failed")
        if self.vector_gauge_projector**2 != self.vector_gauge_projector:
            raise AssertionError("vector gauge complement is not a projector")
        if self.curvature_identity_temporal != sp.zeros(14, 26).row_join(sp.eye(14)):
            raise AssertionError("certified temporal Ncurv table drifted")
        if self.curvature_identity_sharp_temporal != self.curvature_identity_temporal.T:
            raise AssertionError("Ncurv-sharp coordinate dual drifted")
        if self.equation_vector_embedding != self.curvature_identity_sharp_temporal * self.identity_vector_embedding:
            raise AssertionError("q/r vectors were not embedded through Ncurv-sharp")
        if self.relative_r1_temporal.shape != (9, 40):
            raise AssertionError("R1 temporal coefficient has wrong shape")
        if self.relative_r6_sharp_temporal.shape != (14, 24):
            raise AssertionError("R6-sharp temporal coefficient has wrong shape")
        recomputed_product = (
            self.gauge_generator_temporal
            * self.relative_r1_temporal
            * self.curvature_identity_sharp_temporal
            * self.relative_r6_sharp_temporal
        )
        if recomputed_product != self.relative_pair16_product:
            raise AssertionError("stored pair-(1,6) product is not coefficientwise")
        if self.relative_pair16_product != self.vector_gauge_projector:
            raise AssertionError(
                "K R1 NcurvSharp R6sharp does not equal the vector projector"
            )
        if (self.paired_hessian_temporal + self.gauge_scalar_diagonal).rank() != 18:
            raise AssertionError("scalar-retained diagonal rank drifted")
        if self.algebraic_target_complement.rank() != 24:
            raise AssertionError("algebraic numerator target is singular")
        if sp.factor(self.algebraic_target_complement.det()) != 1:
            raise AssertionError("algebraic numerator target determinant drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        restricted = (
            self.gauge_scalar_embedding.T
            * self.gauge_completion_temporal
            * self.gauge_scalar_embedding
        )
        return {
            "schema": "pure-weyl-expanded-relative-witness-scalar-completion-v1",
            "temporal_covector": "dt",
            "central_scalar_basis": list(SCALAR_BASIS_NAMES),
            "paired_hessian_scalar_matrix": _integer_matrix(self.scalar_hessian),
            "paired_hessian_scalar_rank": self.scalar_hessian.rank(),
            "exact_missing_scalar_directions": list(GAUGE_SCALAR_NAMES),
            "minimal_support_local_scalar_diagonal": {
                "operator": "Pi_(h00,f00,v0) K_1(dt) C_1(dt) Pi_(h00,f00,v0)",
                "fibre_order": 0,
                "differential_order": 2,
                "rank": self.gauge_scalar_diagonal.rank(),
                "restricted_matrix": _integer_matrix(restricted),
                "determinant": int(restricted.det()),
                "uses_parallel_cylinder_time_normal_only": True,
                "support_local": True,
            },
            "pair_1_plus_6_explicit_temporal_maps": {
                "relative_orders": {"R1": 0, "R6": 1},
                "ghost_vector_columns": list(VECTOR_GHOST_COLUMNS),
                "curvature_identity_vector_coordinates": "q[3] plus r[3]",
                "R1": "J_vector S_vector^T: X_Eq_sharp[40] -> G_aux[9]",
                "R6sharp": "I_vector (K_vector^T K_vector)^-1 K_vector^T: M_aux[24] -> X_Id_sharp[14]",
                "NcurvSharp_R6sharp": "S_vector (K_vector^T K_vector)^-1 K_vector^T",
                "verified_local_numerator": "K R1 NcurvSharp R6sharp=Pi_vector_gauge",
                "certified_Ncurv_temporal_shape": list(self.curvature_identity_temporal.shape),
                "certified_Ncurv_temporal_matrix": "[0_(14x26),I_14]",
                "NcurvSharp_sha256": _digest(self.curvature_identity_sharp_temporal),
                "R1_shape": list(self.relative_r1_temporal.shape),
                "R1_nonzero_coordinates": [
                    [row, 26 + column, 1]
                    for column, row in enumerate(VECTOR_GHOST_COLUMNS)
                ],
                "R1_sha256": _digest(self.relative_r1_temporal),
                "R6sharp_shape": list(self.relative_r6_sharp_temporal.shape),
                "R6sharp_first_six_rows": _integer_matrix(
                    self.relative_r6_sharp_temporal[:6, :]
                ),
                "R6sharp_sha256": _digest(self.relative_r6_sharp_temporal),
                "coefficientwise_product_defect": sum(
                    int(value != 0)
                    for value in (
                        self.relative_pair16_product - self.vector_gauge_projector
                    )
                ),
                "SO3_intertwining_verified_in_independent_certificate": True,
                "SO3_intertwining_certificate": (
                    "curved_expanded_relative_witness_commutant.json"
                ),
                "finite_order_and_support_local": True,
            },
            "algebraic_numerator_target": {
                "field_diagonal": "Eaux_2(dt)+minimal_scalar_diagonal",
                "field_diagonal_rank": (
                    self.paired_hessian_temporal + self.gauge_scalar_diagonal
                ).rank(),
                "formal_target": "Eaux_2+D_scalar-Pi_vector_gauge",
                "formal_target_rank": self.algebraic_target_complement.rank(),
                "formal_target_determinant": int(
                    sp.factor(self.algebraic_target_complement.det())
                ),
                "is_actual_saddle_Schur_complement": False,
                "missing_factor": (
                    "inverse of the actual 92x92 curvature temporal principal block D is not loaded in this numerator-only certificate"
                ),
                "downstream_temporal_Douglis_certificate": (
                    "curved_expanded_relative_witness_douglis.json"
                ),
                "raw_BC_order": 3,
                "desired_B_Dinverse_C_order": 2,
            },
            "analytic_boundary": {
                "actual_curvature_temporal_diagonal_loaded": False,
                "actual_curvature_temporal_inverse_inserted": False,
                "full_116_by_116_Douglis_symbol_assembled": False,
                "SO3_intertwining_certified_in_separate_certificate": True,
                "arbitrary_covector_characteristic_certified": False,
                "positive_symmetrizer_certified": False,
                "all_lower_order_coefficients_certified": False,
                "all_BV_degrees_green_certified": False,
            },
            "constructive_conclusion": (
                "the three-dimensional incidence defect is exactly the scalar "
                "gauge kernel h00,f00,v0, and the rank-three scalar part of K C "
                "is minimal.  The displayed pair-(1,6) maps realize only the "
                "local numerator B C; this certificate does not load D^{-1}, "
                "so it makes no actual Schur-complement or 116-dimensional "
                "rank claim.  Those temporal statements are checked separately"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
