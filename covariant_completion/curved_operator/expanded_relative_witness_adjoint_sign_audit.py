"""Formal-adjoint and full-covector audit for the pair-(1,6) saddle.

The temporal Douglis candidate uses the central block order

``M[24], X_U[26], X_Eq#[40], Y_U#[26]``.

This module derives its signs from the coefficientwise compact-support rule
``A_I^sharp=(-1)^|I| A_I^T`` rather than assigning them independently.  It
also records the complete *known* arbitrary-covector curvature diagonal and
the exact boundary of the relative maps: ``R1`` is an order-zero bundle map,
whereas the existing ``R6sharp`` table supplies only its temporal first-order
coefficient.  Consequently the current data define a temporal matrix but not
an arbitrary-covector relative saddle.

No Green-theoretic flag is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .expanded_relative_witness_scalar_completion import (
    ExpandedRelativeScalarCompletion,
)
from .weyl_cotton_hyperbolic import (
    ConstraintAdjustedWeylCottonEvolution,
)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ExpandedRelativeWitnessAdjointSignAudit:
    scalar: ExpandedRelativeScalarCompletion
    curvature_principal_coefficients: tuple[sp.Matrix, ...]
    n_principal_coefficients: tuple[sp.Matrix, ...]
    n_sharp_principal_coefficients: tuple[sp.Matrix, ...]
    curvature_d_principal_coefficients: tuple[sp.Matrix, ...]
    temporal_b: sp.Matrix
    temporal_c: sp.Matrix
    temporal_d: sp.Matrix
    temporal_bc: sp.Matrix
    temporal_bd_inverse_c: sp.Matrix
    temporal_field_schur: sp.Matrix
    complete_temporal_symbol: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeWitnessAdjointSignAudit":
        scalar = ExpandedRelativeScalarCompletion.build()
        evolution = ConstraintAdjustedWeylCottonEvolution.build()

        # L and S are normalized as partial_t+spatial principal terms.
        l_coefficients = (sp.eye(26), *evolution.evolution_spatial_coefficients)
        s_coefficients = (sp.eye(14), *evolution.constraint_spatial_coefficients)

        # N=(-R,S): Eq=F+C -> Id.  At principal order R and K have the
        # same coefficient tables.  These are the full four derivative
        # coefficients, with the time coefficient [0,I_14].
        n_coefficients = (
            sp.zeros(14, 26).row_join(sp.eye(14)),
            *(
                (-evolution.source_compatibility_spatial_coefficients[axis]).row_join(
                    evolution.constraint_spatial_coefficients[axis]
                )
                for axis in range(3)
            ),
        )
        n_sharp_coefficients = tuple(-coefficient.T for coefficient in n_coefficients)

        # Exact arbitrary-covector curvature diagonal:
        # diag(L, (diag(L,S))^sharp, L^sharp).
        d_coefficients = tuple(
            sp.diag(
                l_coefficient,
                -l_coefficient.T,
                -s_coefficient.T,
                -l_coefficient.T,
            )
            for l_coefficient, s_coefficient in zip(
                l_coefficients, s_coefficients, strict=True
            )
        )

        b = sp.zeros(24, 92)
        b[:, 26:66] = (
            scalar.gauge_generator_temporal * scalar.relative_r1_temporal
        )
        c = sp.zeros(92, 24)
        c[26:66, :] = (
            n_sharp_coefficients[0] * scalar.relative_r6_sharp_temporal
        )
        d = d_coefficients[0]
        bc = b * c
        bd_inverse_c = b * d.inv() * c
        field_diagonal = scalar.paired_hessian_temporal + scalar.gauge_scalar_diagonal
        field_schur = field_diagonal - bd_inverse_c
        complete = field_diagonal.row_join(b).col_join(c.row_join(d))

        result = ExpandedRelativeWitnessAdjointSignAudit(
            scalar=scalar,
            curvature_principal_coefficients=l_coefficients,
            n_principal_coefficients=n_coefficients,
            n_sharp_principal_coefficients=n_sharp_coefficients,
            curvature_d_principal_coefficients=d_coefficients,
            temporal_b=b,
            temporal_c=c,
            temporal_d=d,
            temporal_bc=bc,
            temporal_bd_inverse_c=bd_inverse_c,
            temporal_field_schur=field_schur,
            complete_temporal_symbol=complete,
        )
        result.verify()
        return result

    def verify(self) -> None:
        scalar = self.scalar
        if len(self.n_principal_coefficients) != 4:
            raise AssertionError("Ncurv full first-order coefficient coverage drifted")
        if any(
            sharp != -primal.T
            for primal, sharp in zip(
                self.n_principal_coefficients,
                self.n_sharp_principal_coefficients,
                strict=True,
            )
        ):
            raise AssertionError("first-order Ncurv formal-adjoint sign failed")
        if self.n_sharp_principal_coefficients[0] != scalar.curvature_identity_sharp_temporal:
            raise AssertionError("scalar completion is not using the formal Ncurv sharp")
        expected_d = sp.diag(sp.eye(26), -sp.eye(40), -sp.eye(26))
        if self.temporal_d != expected_d:
            raise AssertionError("temporal curvature diagonal sign drifted")
        if self.temporal_bc != -scalar.vector_gauge_projector:
            raise AssertionError("the corrected temporal numerator is not -Pi_vector")
        if self.temporal_bd_inverse_c != scalar.vector_gauge_projector:
            raise AssertionError("the corrected temporal Schur term is not +Pi_vector")
        if self.temporal_field_schur != scalar.algebraic_target_complement:
            raise AssertionError("temporal field Schur disagrees with E+Dscalar-Pi")
        if self.temporal_field_schur.rank() != 24:
            raise AssertionError("corrected temporal field Schur is singular")
        if sp.factor(self.temporal_field_schur.det()) != 1:
            raise AssertionError("corrected temporal field Schur determinant drifted")
        if self.complete_temporal_symbol.shape != (116, 116):
            raise AssertionError("corrected temporal symbol has wrong shape")
        if self.complete_temporal_symbol.rank() != 116:
            raise AssertionError("corrected temporal symbol is singular")
        if sp.factor(self.complete_temporal_symbol.det()) != 1:
            raise AssertionError("corrected temporal determinant drifted")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-expanded-relative-witness-adjoint-sign-audit-v1",
            "central_block_order": [
                "M_aux[24]",
                "X_U[26]",
                "X_Eq_sharp[40]",
                "Y_U_sharp[26]",
            ],
            "exact_full_covector_block_formula": {
                "A": "Eaux_2(zeta)+Dscalar_2(zeta)",
                "B": "[0, K_1(zeta) R1, 0]",
                "C": "[0, Ncurv_1^sharp(zeta) R6sharp_1(zeta), 0]^T",
                "D": (
                    "diag(L_26(zeta), -diag(L_26(zeta)^T,S_14(zeta)^T), "
                    "-L_26(zeta)^T)"
                ),
                "Douglis_orders": {"A": 2, "B": 1, "C": 2, "D": 1},
                "types": {
                    "A": "M_aux[24] -> M_aux[24]",
                    "B": "X_U+X_Eq_sharp+Y_U_sharp[92] -> M_aux[24]",
                    "C": "M_aux[24] -> X_U+X_Eq_sharp+Y_U_sharp[92]",
                    "D": "curvature_central[92] -> curvature_central[92]",
                },
            },
            "formal_adjoint_convention": {
                "rule": "A_I^sharp=(-1)^|I| A_I^T for parallel coefficients",
                "Ncurv_order": 1,
                "NcurvSharp_coefficients_equal_minus_transpose": True,
                "coefficient_count": len(self.n_sharp_principal_coefficients),
                "temporal_Ncurv": "[0_(14x26),I_14]",
                "temporal_NcurvSharp": "-[0_(14x26),I_14]^T",
                "temporal_sha256": _digest(self.n_sharp_principal_coefficients[0]),
            },
            "known_arbitrary_covector_curvature_diagonal": {
                "coefficient_count": len(self.curvature_d_principal_coefficients),
                "coefficient_shapes": [list(item.shape) for item in self.curvature_d_principal_coefficients],
                "coefficient_sha256": [
                    _digest(item) for item in self.curvature_d_principal_coefficients
                ],
                "derived_from_exact_L_and_S_tables": True,
            },
            "corrected_temporal_Schur_calculation": {
                "BC": "-Pi_vector_gauge",
                "B_Dinverse_C": "+Pi_vector_gauge",
                "field_Schur": "Eaux_2(dt)+Dscalar_2(dt)-Pi_vector_gauge",
                "field_Schur_rank": self.temporal_field_schur.rank(),
                "field_Schur_determinant": int(sp.factor(self.temporal_field_schur.det())),
                "complete_shape": list(self.complete_temporal_symbol.shape),
                "complete_rank": self.complete_temporal_symbol.rank(),
                "complete_determinant": int(sp.factor(self.complete_temporal_symbol.det())),
                "sha256": _digest(self.complete_temporal_symbol),
            },
            "operator_coverage_boundary": {
                "R1_order_zero_full_bundle_map": True,
                "R1_spatial_coefficients_required": 0,
                "R6sharp_order_one_coefficients_required": 4,
                "R6sharp_coefficients_currently_constructed": 1,
                "R6sharp_missing_spatial_coefficients": 3,
                "R6sharp_covariant_formula_constructed": False,
                "Dscalar_order_two_coefficients_required": 10,
                "Dscalar_coefficients_currently_constructed": 1,
                "Dscalar_cyclic_witness_lift_constructed": False,
                "arbitrary_covector_relative_symbol_defined": False,
                "reason": (
                    "a temporal coefficient does not determine the three spatial "
                    "coefficients of R6sharp or the remaining order-two scalar table"
                ),
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
