"""Current reduction forced by the exact curved auxiliary square.

This is the shared bridge between the retract and current workstreams.  It
does not reconstruct the tangent shift: callers supply the verified
``CurvedAuxiliaryTangentShift`` which is also used to conjugate the BV
differential.

In shifted variables the quadratic gauge-invariant action is

``L_aux^(2)=L_met^(2)+1/2 <f_hat,A_g f_hat>``.

The second summand is algebraic, so its canonical presymplectic potential is
zero.  On the retract image ``f_hat=delta f_hat=0``.  Therefore the minimal
shifted-coordinate currents agree exactly.  In original variables the extra
potential is the Green concomitant of the shared finite-order shift; it also
vanishes on the retract image.  What this lemma deliberately does not supply
is the Q-exact gauge-fixing/nonminimal current or an instantiated causal
Green/current comparison.  Those remain necessary for full promotion.
"""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.curved_operator import ActionDerivedAuxiliaryHessian
from covariant_completion.curved_retract import (
    CurvedAuxiliaryEOMShift,
    CurvedAuxiliaryTangentShift,
)


@dataclass(frozen=True)
class ShiftedActionCurrentReduction:
    """Exact minimal current reduction in the shared shifted variables."""

    action_hessian: ActionDerivedAuxiliaryHessian
    eom_shift: CurvedAuxiliaryEOMShift

    @staticmethod
    def from_action_hessian(
        action_hessian: ActionDerivedAuxiliaryHessian,
    ) -> "ShiftedActionCurrentReduction":
        """Build from the operator workstream's action factorization.

        ``action_hessian`` owns the same verified tangent shift used by the
        retract.  This consumer checks stable interfaces without reconstructing
        that shift or repeating its exhaustive jet battery.
        """

        result = ShiftedActionCurrentReduction(
            action_hessian=action_hessian,
            eom_shift=CurvedAuxiliaryEOMShift.build(),
        )
        result.verify(reverify_hessian=False)
        return result

    @staticmethod
    def from_verified_shift(
        tangent_shift: CurvedAuxiliaryTangentShift,
    ) -> "ShiftedActionCurrentReduction":
        """Compatibility constructor which still uses the action producer."""

        return ShiftedActionCurrentReduction.from_action_hessian(
            ActionDerivedAuxiliaryHessian.build(shift=tangent_shift)
        )

    def verify(self, *, reverify_hessian: bool = True) -> None:
        if reverify_hessian:
            self.action_hessian.verify()
        self.eom_shift.verify()
        metric_symbol, vector_symbol = self.action_hessian.shift.principal_symbol()
        if metric_symbol.shape != (10, 10):
            raise AssertionError("the shared metric tangent shift has the wrong shape")
        if vector_symbol.shape != (10, 4):
            raise AssertionError("the shared vector tangent shift has the wrong shape")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-shifted-curved-action-current-reduction-v1",
            "shared_shift": {
                "operator": "S=D[A_g^{-1}G^b]_(gbar,0)",
                "producer": (
                    "covariant_completion.curved_retract."
                    "CurvedAuxiliaryTangentShift"
                ),
                "curvature_terms_included": True,
                "variation_of_mass_inverse_included": True,
                "not_reconstructed_by_current_workstream": True,
            },
            "action_hessian": {
                "producer": (
                    "covariant_completion.curved_operator."
                    "ActionDerivedAuxiliaryHessian"
                ),
                "factorization": (
                    "E_aux,cyl=U_shift^sharp diag(B_lin,A_g,0) U_shift"
                ),
                "formal_self_adjoint_by_construction": True,
                "eliminated_vector_density_boundary_identity": True,
            },
            "shifted_quadratic_action": (
                "L_aux^(2)=L_met^(2)+1/2<f_hat,A_g f_hat>"
            ),
            "presymplectic_representatives": {
                "theta_metric": (
                    "canonical variational boundary homotopy of L_met^(2)"
                ),
                "theta_auxiliary_shifted": "theta_metric+theta_genaux",
                "theta_genaux": "zero (A_g block is algebraic)",
                "theta_auxiliary_original_variables": (
                    "theta_metric-J_S(A_g f_hat,delta(h,v))+delta B_elim"
                ),
                "J_S_identity": (
                    "d J_S(l,r)=<l,S r>-<S^sharp l,r> for the exact shared S"
                ),
                "eliminated_vector_boundary": (
                    "delta of the explicit local B^a from "
                    "EliminatedVectorDensityIdentity"
                ),
            },
            "generalized_auxiliary_sector": {
                "differential_order": 0,
                "canonical_presymplectic_potential": "zero",
                "canonical_presymplectic_current": "zero",
            },
            "retract_image": {
                "f_hat": "zero",
                "delta_f_hat": "zero",
                "minimal_shifted_potential_pullback": "theta_met",
                "minimal_shifted_current_pullback": "omega_met",
                "original_variable_extra_term": (
                    "J_S vanishes because f_hat=0; delta B_elim is variationally exact"
                ),
            },
            "minimal_shifted_action_current_identity": True,
            "minimal_curved_auxiliary_potential_derived": True,
            "minimal_curved_metric_potential_derived": True,
            "support_local": True,
            "full_curved_current_comparison": False,
            "remaining": [
                "emit the Q-exact gauge-fixing/nonminimal improvement",
                "instantiate the curved Green/current and slab-current identities",
            ],
        }
