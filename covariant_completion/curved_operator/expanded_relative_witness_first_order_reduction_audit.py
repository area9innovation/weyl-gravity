"""Independent exact audit of the pair-(1,6) first-order reduction.

The local 212-state principal-model reduction has two related, but different,
prolongation maps.  The coefficientwise polynomial map is

``T_op(zeta)(m,x)=(m,zeta_0 m,...,zeta_3 m,x)``.

It intertwines the first-order reduction of the weighted principal model
(including the algebraic ``-p_0`` definition term) with the 116-row weighted
principal operator.  It does not supply the still-open curved lower-order
completion.  For the homogeneous aligned characteristic pencil one instead
uses the graded map

``T(z)(m,x)=(0,-z m,m,0,0,x)``.

The explicit generalized eigenvector is *not* in the fixed image of
``T(1)``.  It is in its first spectral jet:

``u=T(1)a_0``, ``v=T(1)a_1+T'(1)a_0``.

The vectors ``a_0,a_1`` form an exact polynomial Jordan chain for the
original 116-square weighted symbol.  This distinction is important: it
both rejects the naive fixed-constraint claim and proves that the Jordan
defect is not an artifact of the added gradient equations.

No Green-theoretic flag is promoted here.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .expanded_relative_witness_first_order_reduction import (
    COMPLETE_RANK,
    CORE_ROW_START,
    CURVATURE_RANK,
    FIELD_RANK,
    REDUCED_RANK,
    ExpandedRelativeFirstOrderReduction,
)


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableSparseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


def _nonzero_count(matrix: sp.MatrixBase) -> int:
    # The block-elimination audit contains harmless ``1/tau`` rational
    # expressions.  Normalize them before deciding whether a coefficient
    # vanishes; structural ``!= 0`` would count uncancelled copies such as
    # ``-2*tau+rho**2/tau-(-2*tau**2+rho**2)/tau``.
    return sum(int(sp.cancel(value) != 0) for value in matrix)


def _embed_core(matrix: sp.MatrixBase) -> sp.Matrix:
    result = sp.zeros(REDUCED_RANK, matrix.cols)
    result[CORE_ROW_START:, :] = matrix
    return result


def _operator_prolongation(
    covector: tuple[sp.Expr, sp.Expr, sp.Expr, sp.Expr],
) -> sp.Matrix:
    """The polynomial principal-model prolongation ``(m,x)->(m,p,x)``."""

    result = sp.zeros(REDUCED_RANK, COMPLETE_RANK)
    result[:FIELD_RANK, :FIELD_RANK] = sp.eye(FIELD_RANK)
    for derivative, value in enumerate(covector):
        row = FIELD_RANK * (derivative + 1)
        result[row : row + FIELD_RANK, :FIELD_RANK] = (
            value * sp.eye(FIELD_RANK)
        )
    result[5 * FIELD_RANK :, FIELD_RANK:] = sp.eye(CURVATURE_RANK)
    return result


def _spectral_prolongation(z: sp.Expr) -> sp.Matrix:
    """Leading graded prolongation for ``P((-z,1,0,0))``."""

    result = sp.zeros(REDUCED_RANK, COMPLETE_RANK)
    result[FIELD_RANK : 2 * FIELD_RANK, :FIELD_RANK] = (
        -z * sp.eye(FIELD_RANK)
    )
    result[2 * FIELD_RANK : 3 * FIELD_RANK, :FIELD_RANK] = sp.eye(
        FIELD_RANK
    )
    result[5 * FIELD_RANK :, FIELD_RANK:] = sp.eye(CURVATURE_RANK)
    return result


@dataclass(frozen=True)
class ExpandedRelativeFirstOrderReductionAudit:
    reduction: ExpandedRelativeFirstOrderReduction
    operator_intertwining_defect: int
    spectral_intertwining_defect: int
    schur_elimination_defect: int
    polynomial_eigenvector_defect: int
    polynomial_generalized_defect: int
    reduced_eigenvector_lift_defect: int
    reduced_generalized_tangent_lift_defect: int
    generalized_fixed_image_constraint_defect: int
    determinant_pivot_power: int
    determinant_column_scaling_power: int
    determinant_net_power: int
    determinant_permutation_parity: int
    original_eigenvector: sp.Matrix
    original_generalized_vector: sp.Matrix

    @staticmethod
    def build() -> "ExpandedRelativeFirstOrderReductionAudit":
        reduction = ExpandedRelativeFirstOrderReduction.build()
        full = reduction.full_symbol
        tau, xi1, xi2, xi3 = full.covector
        covector = (tau, xi1, xi2, xi3)

        complete_operator = (
            tau * reduction.temporal_coefficient
            + xi1 * reduction.spatial_coefficients[0]
            + xi2 * reduction.spatial_coefficients[1]
            + xi3 * reduction.spatial_coefficients[2]
            + reduction.zeroth_coefficient
        )
        operator_prolongation = _operator_prolongation(covector)
        weighted = full.symbol(covector, separated=True)
        operator_defect = _nonzero_count(
            complete_operator * operator_prolongation - _embed_core(weighted)
        )

        z = sp.Symbol("expanded_relative_reduction_spectral_z")
        spectral_pencil = (
            reduction.spatial_coefficients[0]
            - z * reduction.temporal_coefficient
        )
        spectral_prolongation = _spectral_prolongation(z)
        original_pencil = full.symbol((-z, 1, 0, 0), separated=True)
        spectral_defect = _nonzero_count(
            spectral_pencil * spectral_prolongation
            - _embed_core(original_pencil)
        )

        # Exact block elimination behind
        # det(tau A0+rho A1)=tau^72 det(P_weighted(tau,rho)).
        rho = sp.Symbol("expanded_relative_reduction_rho")
        aligned_reduced = (
            tau * reduction.temporal_coefficient
            + rho * reduction.spatial_coefficients[0]
        )
        core = aligned_reduced[CORE_ROW_START:, :]
        p0 = slice(FIELD_RANK, 2 * FIELD_RANK)
        p1 = slice(2 * FIELD_RANK, 3 * FIELD_RANK)
        curvature = slice(5 * FIELD_RANK, REDUCED_RANK)
        eliminated = (
            core[:, p0] + rho / tau * core[:, p1]
        ).row_join(core[:, curvature])
        aligned_weighted = full.symbol((tau, rho, 0, 0), separated=True)
        scaled_weighted = aligned_weighted * sp.diag(
            sp.eye(FIELD_RANK) / tau,
            sp.eye(CURVATURE_RANK),
        )
        schur_defect = _nonzero_count(eliminated - scaled_weighted)

        a0 = sp.zeros(COMPLETE_RANK, 1)
        a0[18] = 2
        a1 = sp.zeros(COMPLETE_RANK, 1)
        a1[8] = 1
        q_at_one = original_pencil.subs(z, 1)
        q_prime_at_one = original_pencil.diff(z).subs(z, 1)
        polynomial_eigen_defect = _nonzero_count(q_at_one * a0)
        polynomial_generalized_defect = _nonzero_count(
            q_at_one * a1 + q_prime_at_one * a0
        )

        t_at_one = spectral_prolongation.subs(z, 1)
        t_prime_at_one = spectral_prolongation.diff(z).subs(z, 1)
        u = reduction.jordan_eigenvector
        v = reduction.jordan_generalized_vector
        eigen_lift_defect = _nonzero_count(u - t_at_one * a0)
        generalized_lift_defect = _nonzero_count(
            v - t_at_one * a1 - t_prime_at_one * a0
        )

        # At z=1 every vector in the fixed image obeys p0+p1=0.  The
        # generalized vector violates this by -2 e_18; this is exactly the
        # T'(1)a0 tangent correction, not a failure of polynomial
        # compatibility.
        fixed_image_constraint = (
            v[FIELD_RANK : 2 * FIELD_RANK, :]
            + v[2 * FIELD_RANK : 3 * FIELD_RANK, :]
        )
        fixed_image_defect = _nonzero_count(fixed_image_constraint)

        result = ExpandedRelativeFirstOrderReductionAudit(
            reduction=reduction,
            operator_intertwining_defect=operator_defect,
            spectral_intertwining_defect=spectral_defect,
            schur_elimination_defect=schur_defect,
            polynomial_eigenvector_defect=polynomial_eigen_defect,
            polynomial_generalized_defect=polynomial_generalized_defect,
            reduced_eigenvector_lift_defect=eigen_lift_defect,
            reduced_generalized_tangent_lift_defect=generalized_lift_defect,
            generalized_fixed_image_constraint_defect=fixed_image_defect,
            determinant_pivot_power=96,
            determinant_column_scaling_power=-24,
            determinant_net_power=72,
            determinant_permutation_parity=(24 * 72) % 2,
            original_eigenvector=a0,
            original_generalized_vector=a1,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.operator_intertwining_defect:
            raise AssertionError("full differential reduction does not intertwine")
        if self.spectral_intertwining_defect:
            raise AssertionError("graded characteristic reduction does not intertwine")
        if self.schur_elimination_defect:
            raise AssertionError("aligned block-elimination identity failed")
        if self.polynomial_eigenvector_defect:
            raise AssertionError("original polynomial eigenvector failed")
        if self.polynomial_generalized_defect:
            raise AssertionError("original polynomial Jordan-chain identity failed")
        if self.reduced_eigenvector_lift_defect:
            raise AssertionError("reduced eigenvector is not the spectral lift")
        if self.reduced_generalized_tangent_lift_defect:
            raise AssertionError("reduced generalized vector is not the tangent lift")
        if self.generalized_fixed_image_constraint_defect != 1:
            raise AssertionError("fixed-image constraint distinction drifted")
        if (
            self.determinant_pivot_power,
            self.determinant_column_scaling_power,
            self.determinant_net_power,
            self.determinant_permutation_parity,
        ) != (96, -24, 72, 0):
            raise AssertionError("determinant exponent/sign ledger drifted")

        fixed_defect = (
            self.reduction.jordan_generalized_vector[
                FIELD_RANK : 2 * FIELD_RANK, :
            ]
            + self.reduction.jordan_generalized_vector[
                2 * FIELD_RANK : 3 * FIELD_RANK, :
            ]
        )
        expected = sp.zeros(FIELD_RANK, 1)
        expected[18] = -2
        if fixed_defect != expected:
            raise AssertionError("generalized fixed-image defect changed")

    def certificate(self) -> dict[str, object]:
        self.verify()
        reduction = self.reduction
        return {
            "schema": "pure-weyl-expanded-relative-first-order-reduction-audit-v1",
            "scope": {
                "relative_branch": "pair-(1,6)",
                "R6sharp_extension": "R6sharp_0 nabla_0 (spatial coefficients zero)",
                "scalar_branch": "D_alt=-2 Pi_(h00,f00,v0)",
                "full_invariant_spatial_R6sharp_family_tested": False,
            },
            "principal_model_operator_intertwining": {
                "operator": "tau A0+xi_i Ai+Azeroth",
                "prolongation": "T_op(m,x)=(m,tau m,xi_1 m,xi_2 m,xi_3 m,x)",
                "identity": "L_op(zeta) T_op(zeta)=0_[96] direct-sum P_weighted(zeta)",
                "coefficientwise_defect": self.operator_intertwining_defect,
                "curved_lower_order_completion_included": False,
                "prolongation_sha256": _digest(
                    _operator_prolongation(reduction.full_symbol.covector)
                ),
            },
            "aligned_determinant_audit": {
                "block_elimination_identity": (
                    "S=[P_field/tau,P_curvature] after p1=(rho/tau)p0, p2=p3=0"
                ),
                "schur_elimination_defect": self.schur_elimination_defect,
                "definition_and_gradient_pivot_power": self.determinant_pivot_power,
                "field_column_scaling_power": self.determinant_column_scaling_power,
                "net_tau_power": self.determinant_net_power,
                "column_permutation_parity": self.determinant_permutation_parity,
                "identity": "det(tau A0+rho A1)=tau^72 det(P_weighted(tau,rho))",
                "sign": "+1",
                "polynomial_extension_across_tau_zero": True,
            },
            "intrinsic_polynomial_Jordan_chain": {
                "original_pencil": "Q(z)=P_weighted((-z,1,0,0))",
                "a0_nonzero_entries": [[18, "2"]],
                "a1_nonzero_entries": [[8, "1"]],
                "Q1_a0_defect": self.polynomial_eigenvector_defect,
                "Q1_a1_plus_Qprime1_a0_defect": self.polynomial_generalized_defect,
                "spectral_prolongation": (
                    "T(z)(m,x)=(0,-z m,m,0,0,x)"
                ),
                "spectral_intertwining_identity": (
                    "(A1-z A0)T(z)=0_[96] direct-sum Q(z)"
                ),
                "spectral_intertwining_defect": self.spectral_intertwining_defect,
                "u_equals_T1_a0_defect": self.reduced_eigenvector_lift_defect,
                "v_equals_T1_a1_plus_Tprime1_a0_defect": (
                    self.reduced_generalized_tangent_lift_defect
                ),
                "u_in_fixed_spectral_prolongation_image": True,
                "v_in_fixed_spectral_prolongation_image": False,
                "v_in_first_spectral_jet": True,
                "fixed_image_constraint_defect_nonzero_entries": [[18, "-2"]],
                "constraint_artifact": False,
            },
            "positive_symmetrizer_scope": {
                "explicit_212_reduction_obstructed": True,
                "reason": "nontrivial +1 Jordan chain in A0^-1 A1",
                "intrinsic_polynomial_elementary_divisor_length_at_least": 2,
                "strong_polynomial_linearizations_preserving_finite_elementary_divisors_obstructed": True,
                "arbitrary_support_local_first_order_realizations_obstructed": False,
                "generalized_or_compositional_Green_hyperbolicity_obstructed": False,
                "full_invariant_spatial_R6sharp_family_obstructed": False,
            },
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
