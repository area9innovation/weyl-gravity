"""Actual temporal Douglis block for the pair-(1,6) relative candidate.

This module inserts the curvature temporal diagonal which was deliberately
missing from :mod:`expanded_relative_witness_scalar_completion`.  In the
split mapping-cylinder coordinates the three central curvature blocks are

``pF Ecurv = +I_26``,
``NcurvSharp iCsharp+pFsharp EcurvSharp = -I_40``,
``EcurvSharp pFsharp = -I_26``.

The minus signs are the principal first-order formal-adjoint signs.  Thus
``D=diag(I_26,-I_40,-I_26)`` and the pair-(1,6) Schur term is genuinely
``B D^{-1} C=-Pi_vector``, not the previously certified numerator ``B C``.
With the rank-three scalar auxiliary diagonal ansatz, the assembled exact
temporal Douglis matrix is nonsingular.  This remains only a temporal-symbol
candidate: the scalar diagonal has not been lifted to a complete cyclic
witness, and no arbitrary-covector or symmetrizer theorem is asserted.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from .expanded_relative_witness_scalar_completion import (
    ExpandedRelativeScalarCompletion,
)
from .weyl_cotton_block_green_witness import WeylCottonBlockGreenWitness


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class ExpandedRelativeDouglisCandidate:
    scalar_completion: ExpandedRelativeScalarCompletion
    curvature_temporal_diagonal: sp.Matrix
    curvature_temporal_inverse: sp.Matrix
    off_diagonal_b: sp.Matrix
    off_diagonal_c: sp.Matrix
    actual_schur_term: sp.Matrix
    field_diagonal: sp.Matrix
    field_schur_complement: sp.Matrix
    complete_temporal_symbol: sp.Matrix
    complete_rank: int
    complete_determinant: sp.Expr

    @staticmethod
    def build() -> "ExpandedRelativeDouglisCandidate":
        scalar = ExpandedRelativeScalarCompletion.build()
        curvature = WeylCottonBlockGreenWitness.build()
        curvature.verify()

        # The exact adjusted equations are L U=partial_t U+..., and the
        # subsidiary equations are S c=partial_t c+....  Cotangent blocks
        # acquire the first-order formal-adjoint sign.
        primal_state = sp.eye(26)
        equation_dual = -sp.diag(sp.eye(26), sp.eye(14))
        state_dual = -sp.eye(26)
        diagonal = sp.diag(primal_state, equation_dual, state_dual)
        diagonal_inverse = diagonal.inv()

        # Central order is M[24], X_U[26], X_Eq#[40], Y_U#[26].  Pair 1
        # contributes B=K R1 into X_Eq#; pair 6 contributes
        # C=N# R6# from M.
        b = sp.zeros(24, 92)
        b[:, 26:66] = (
            scalar.gauge_generator_temporal * scalar.relative_r1_temporal
        )
        c = sp.zeros(92, 24)
        c[26:66, :] = (
            scalar.curvature_identity_sharp_temporal
            * scalar.relative_r6_sharp_temporal
        )
        schur_term = b * diagonal_inverse * c
        field_diagonal = (
            scalar.paired_hessian_temporal + scalar.gauge_scalar_diagonal
        )
        field_schur = field_diagonal - schur_term
        complete = field_diagonal.row_join(b).col_join(c.row_join(diagonal))

        # Compute the exact determinant through the standard block identity;
        # rank is checked directly on the assembled 116-by-116 matrix.
        determinant = sp.factor(diagonal.det() * field_schur.det())
        result = ExpandedRelativeDouglisCandidate(
            scalar_completion=scalar,
            curvature_temporal_diagonal=diagonal,
            curvature_temporal_inverse=diagonal_inverse,
            off_diagonal_b=b,
            off_diagonal_c=c,
            actual_schur_term=schur_term,
            field_diagonal=field_diagonal,
            field_schur_complement=field_schur,
            complete_temporal_symbol=complete,
            complete_rank=complete.rank(),
            complete_determinant=determinant,
        )
        result.verify()
        return result

    def verify(self) -> None:
        scalar = self.scalar_completion
        expected_d = sp.diag(sp.eye(26), -sp.eye(40), -sp.eye(26))
        if self.curvature_temporal_diagonal != expected_d:
            raise AssertionError("curvature temporal diagonal signs drifted")
        if (
            self.curvature_temporal_diagonal * self.curvature_temporal_inverse
            != sp.eye(92)
        ):
            raise AssertionError("curvature temporal diagonal has no inverse")
        if self.actual_schur_term != -scalar.vector_gauge_projector:
            raise AssertionError("B D^-1 C is not minus the vector projector")
        if self.field_schur_complement != (
            self.field_diagonal + scalar.vector_gauge_projector
        ):
            raise AssertionError("actual field Schur sign drifted")
        if self.field_schur_complement.rank() != 24:
            raise AssertionError("actual temporal field Schur block is singular")
        if sp.factor(self.field_schur_complement.det()) != 1:
            raise AssertionError("actual temporal field Schur determinant drifted")
        if self.complete_temporal_symbol.shape != (116, 116):
            raise AssertionError("complete central Douglis symbol has wrong shape")
        if self.complete_rank != 116 or self.complete_determinant != 1:
            raise AssertionError("complete temporal Douglis symbol is singular")

    def certificate(self) -> dict[str, object]:
        self.verify()
        return {
            "schema": "pure-weyl-expanded-relative-witness-douglis-temporal-v1",
            "block_order": [
                "M_aux[24]",
                "X_U[26]",
                "X_Eq_sharp[40]",
                "Y_U_sharp[26]",
            ],
            "Douglis_weights": {
                "row_weights": {"M_aux": 1, "curvature": 1},
                "column_weights": {"M_aux": 1, "curvature": 0},
                "principal_orders": {"A": 2, "B": 1, "C": 2, "D": 1},
                "all_four_blocks_principal": True,
            },
            "actual_curvature_temporal_diagonal": {
                "formula": "diag(+I_26,-I_40,-I_26)",
                "source": (
                    "constraint-adjusted L_26 and S_14 temporal identities; "
                    "minus signs from first-order formal adjoints on Eq# and U#"
                ),
                "shape": list(self.curvature_temporal_diagonal.shape),
                "rank": self.curvature_temporal_diagonal.rank(),
                "determinant": int(self.curvature_temporal_diagonal.det()),
                "inverse_equals_itself": (
                    self.curvature_temporal_inverse
                    == self.curvature_temporal_diagonal
                ),
                "sha256": _digest(self.curvature_temporal_diagonal),
            },
            "actual_pair16_Schur_term": {
                "formula": "B D^-1 C",
                "B_shape": list(self.off_diagonal_b.shape),
                "C_shape": list(self.off_diagonal_c.shape),
                "rank": self.actual_schur_term.rank(),
                "equals_minus_vector_gauge_projector": True,
                "defect": sum(
                    int(value != 0)
                    for value in (
                        self.actual_schur_term
                        + self.scalar_completion.vector_gauge_projector
                    )
                ),
                "differential_order": 2,
                "sha256": _digest(self.actual_schur_term),
            },
            "assembled_temporal_Douglis_symbol": {
                "shape": list(self.complete_temporal_symbol.shape),
                "rank": self.complete_rank,
                "determinant": int(self.complete_determinant),
                "rank_defect": 116 - self.complete_rank,
                "field_Schur_rank": self.field_schur_complement.rank(),
                "field_Schur_determinant": int(
                    sp.factor(self.field_schur_complement.det())
                ),
                "sha256": _digest(self.complete_temporal_symbol),
            },
            "scope_and_open_work": {
                "rank3_scalar_diagonal_lifted_to_cyclic_all_row_witness": False,
                "SO3_intertwining_certificate": (
                    "curved_expanded_relative_witness_commutant.json"
                ),
                "arbitrary_covector_characteristic_certified": False,
                "positive_symmetrizer_certified": False,
                "lower_order_completion_certified": False,
                "all_BV_degrees_certified": False,
            },
            "constructive_conclusion": (
                "with the explicit rank-three scalar diagonal ansatz, the actual "
                "curvature temporal inverse corrects the pair-(1,6) numerator sign "
                "and yields a nonsingular 116-dimensional temporal Douglis symbol; "
                "the all-row cyclic lift and hyperbolicity tests remain open"
            ),
            "prolonged_green_witness": False,
            "curvature_causal_green_operators": False,
            "causal_green_homotopy": False,
            "warranted_atomic_flags": [],
            "status_flags_promoted": [],
            "fail_closed": True,
        }
