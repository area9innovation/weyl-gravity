"""Aggregate the curved-operator workstream without crossing its boundary."""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.auxiliary_witness import OrdinaryDerivativeWeylSystem

from .covariant_action import CovariantAuxiliaryAction
from .derivative_normal_form import ParallelCylinderNormalForm
from .globalization_lemma import CurvedOperatorGlobalization


@dataclass(frozen=True)
class CurvedOperatorIdentityStatus:
    action: CovariantAuxiliaryAction
    normal_form: ParallelCylinderNormalForm
    globalization: CurvedOperatorGlobalization
    curved_hessian_expanded: bool = False
    curved_companion_expanded: bool = False
    curved_q_squared_zero: bool = False
    curved_qw_identity_zero: bool = False
    curved_field_adjoint_defect_zero: bool = False
    curved_ghost_adjoint_defect_zero: bool = False
    curved_witness_adjoint_defect_zero: bool = False

    @staticmethod
    def build() -> "CurvedOperatorIdentityStatus":
        # Reverify the exact symbol theorem as an input to this workstream.
        OrdinaryDerivativeWeylSystem.build().verify()
        result = CurvedOperatorIdentityStatus(
            action=CovariantAuxiliaryAction.build(),
            normal_form=ParallelCylinderNormalForm.build(),
            globalization=CurvedOperatorGlobalization.build(),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.action.verify()
        self.normal_form.verify()
        self.globalization.verify()
        if self.complete:
            required = (
                self.curved_hessian_expanded,
                self.curved_companion_expanded,
                self.curved_q_squared_zero,
                self.curved_qw_identity_zero,
                self.curved_field_adjoint_defect_zero,
                self.curved_ghost_adjoint_defect_zero,
                self.curved_witness_adjoint_defect_zero,
                self.globalization.complete,
            )
            if not all(required):
                raise AssertionError("curved operator identity promoted incompletely")

    @property
    def complete(self) -> bool:
        return all(
            (
                self.curved_hessian_expanded,
                self.curved_companion_expanded,
                self.curved_q_squared_zero,
                self.curved_qw_identity_zero,
                self.curved_field_adjoint_defect_zero,
                self.curved_ghost_adjoint_defect_zero,
                self.curved_witness_adjoint_defect_zero,
                self.globalization.complete,
            )
        )

    def certificate(self) -> dict[str, object]:
        self.verify()
        promotion_flags = {
            "curved_hessian_expanded": self.curved_hessian_expanded,
            "curved_companion_expanded": self.curved_companion_expanded,
            "curved_Q_squared_zero": self.curved_q_squared_zero,
            "curved_QW_plus_WQ_minus_P_zero": self.curved_qw_identity_zero,
            "curved_field_adjoint_defect_zero": self.curved_field_adjoint_defect_zero,
            "curved_ghost_adjoint_defect_zero": self.curved_ghost_adjoint_defect_zero,
            "curved_witness_adjoint_defect_zero": self.curved_witness_adjoint_defect_zero,
            "all_degree_wave_symbol_defects_zero": True,
            "globalization_coverage_complete": self.globalization.complete,
        }
        return {
            "schema": "pure-weyl-curved-operator-identity-status-v1",
            "exact_inputs_now": {
                "nonlinear_covariant_action": True,
                "cylinder_background_solution": True,
                "linearized_curved_gauge_map": True,
                "background_auxiliary_Lie_derivative_included": True,
                "flat_limit_matches_symbol_model": True,
                "parallel_curvature_derivative_normal_form": True,
                "all_degree_wave_symbol_defects": 0,
            },
            "promotion_criteria": {
                "curved_hessian_expanded": self.curved_hessian_expanded,
                "curved_companion_expanded": self.curved_companion_expanded,
                "curved_Q_squared": (
                    "zero" if self.curved_q_squared_zero else "not yet evaluated"
                ),
                "curved_QW_plus_WQ_minus_P": (
                    "zero" if self.curved_qw_identity_zero else "not yet evaluated"
                ),
                "curved_field_adjoint_defect": (
                    "zero"
                    if self.curved_field_adjoint_defect_zero
                    else "not yet evaluated"
                ),
                "curved_ghost_adjoint_defect": (
                    "zero"
                    if self.curved_ghost_adjoint_defect_zero
                    else "not yet evaluated"
                ),
                "curved_witness_adjoint_defect": (
                    "zero"
                    if self.curved_witness_adjoint_defect_zero
                    else "not yet evaluated"
                ),
                "globalization_coverage": (
                    "complete" if self.globalization.complete else "incomplete"
                ),
            },
            "promotion_flags": promotion_flags,
            "blocking_criteria": [
                name for name, value in promotion_flags.items() if not value
            ],
            "curved_operator_identity": self.complete,
            "next_exact_step": (
                "differentiate the displayed covariant action and gauge-fixing "
                "density to emit E_aux,cyl and C_aux,cyl in the canonical normal form, "
                "then evaluate the globalization ledger"
            ),
            "fail_closed": True,
        }
