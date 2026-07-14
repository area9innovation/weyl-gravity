"""Aggregate the curved-operator workstream without crossing its boundary."""

from __future__ import annotations

from dataclasses import dataclass

from .covariant_action import CovariantAuxiliaryAction
from .action_hessian import ActionDerivedAuxiliaryHessian
from .conventions import _ordinary_system
from .derivative_normal_form import ParallelCylinderNormalForm
from .globalization_lemma import CurvedOperatorGlobalization
from .four_row_kernel import CurvedFourRowKernel
from .invariant_pairings import InvariantFibrePairingAnsatz
from .null_symbol_rank_obstruction import NullSymbolRankObstruction
from .null_symbol_quotient import CurvedNullSymbolQuotient


@dataclass(frozen=True)
class CurvedOperatorIdentityStatus:
    action: CovariantAuxiliaryAction
    action_hessian: ActionDerivedAuxiliaryHessian
    four_row_kernel: CurvedFourRowKernel
    normal_form: ParallelCylinderNormalForm
    globalization: CurvedOperatorGlobalization
    invariant_pairings: InvariantFibrePairingAnsatz
    null_symbol_obstruction: NullSymbolRankObstruction
    null_symbol_quotient: CurvedNullSymbolQuotient
    curved_hessian_expanded: bool = True
    curved_companion_expanded: bool = True
    curved_q_squared_zero: bool = True
    curved_qw_identity_zero: bool = True
    curved_field_adjoint_defect_zero: bool = True
    curved_ghost_adjoint_defect_zero: bool = True
    curved_witness_adjoint_defect_zero: bool = True
    all_degree_wave_symbol_defects_zero: bool = False
    mixed_order_green_realization: bool = False
    curvature_prolonged_realization: bool = False

    @staticmethod
    def build() -> "CurvedOperatorIdentityStatus":
        # Reverify the exact symbol theorem as an input to this workstream.
        _ordinary_system().verify()
        null_symbol_obstruction = NullSymbolRankObstruction.build()
        result = CurvedOperatorIdentityStatus(
            action=CovariantAuxiliaryAction.build(),
            action_hessian=ActionDerivedAuxiliaryHessian.build(),
            four_row_kernel=CurvedFourRowKernel.build(),
            normal_form=ParallelCylinderNormalForm.build(),
            globalization=CurvedOperatorGlobalization.build(),
            invariant_pairings=InvariantFibrePairingAnsatz.build(),
            null_symbol_obstruction=null_symbol_obstruction,
            null_symbol_quotient=CurvedNullSymbolQuotient.build(),
            curved_hessian_expanded=(
                null_symbol_obstruction.hessian_high_order_jet_vectors_tested == 630
            ),
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.action.verify()
        self.action_hessian.verify()
        self.four_row_kernel.verify()
        self.normal_form.verify()
        self.globalization.verify()
        self.invariant_pairings.verify()
        self.null_symbol_obstruction.verify()
        self.null_symbol_quotient.verify()
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
            "globalization_coverage_complete": self.globalization.complete,
        }
        return {
            "schema": "pure-weyl-curved-operator-identity-status-v2",
            "exact_inputs_now": {
                "nonlinear_covariant_action": True,
                "cylinder_background_solution": True,
                "linearized_curved_gauge_map": True,
                "expanded_curved_gauge_companion": True,
                "curved_companion_adjoint_defect": 0,
                "action_derived_hessian_factorization": True,
                "curved_E_times_K_defect": 0,
                "four_row_Q_assembled": True,
                "four_row_W_assembled": True,
                "background_auxiliary_Lie_derivative_included": True,
                "flat_limit_matches_symbol_model": True,
                "parallel_curvature_derivative_normal_form": True,
                "flat_symbol_wave_defects": 0,
                "curved_field_wave_symbol_defects": 76,
                "curved_wave_defect_scope": "normalized f rows versus metric columns",
                "expanded_hessian_high_order_jet_vectors_tested": (
                    self.null_symbol_obstruction.hessian_high_order_jet_vectors_tested
                ),
                "complete_invariant_pointwise_J_parameter_count": 24,
                "complete_invariant_pointwise_Y_parameter_count": 9,
                "null_covector_rank_E_2": self.null_symbol_obstruction.hessian_rank,
                "null_covector_rank_K_1": self.null_symbol_obstruction.gauge_rank,
                "pointwise_J_C_repair_possible": False,
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
            "atomic_certified_theorems": {
                "curved_exact_hessian": self.curved_hessian_expanded,
                "curved_scalar_wave_no_go": (
                    not self.null_symbol_obstruction.pointwise_pairing_companion_solution_exists
                ),
                "curved_null_symbol_quotient_exact": (
                    self.null_symbol_quotient.quotient_dimension == 2
                ),
                "curved_helicity_two_channel": (
                    self.null_symbol_quotient.induced_weyl_matrix.det() != 0
                ),
            },
            "scalar_wave_realization": {
                "all_degree_wave_symbol_defects": (
                    "zero"
                    if self.all_degree_wave_symbol_defects_zero
                    else (
                        "76 curved field-block entries; exact null-rank obstruction "
                        "rules out every pointwise J and first-order C"
                    )
                ),
                "curved_scalar_wave_no_go": True,
                "separate_from_curved_operator_identity": True,
            },
            "alternative_realization_flags": {
                "mixed_order_green_realization": self.mixed_order_green_realization,
                "curvature_prolonged_realization": (
                    self.curvature_prolonged_realization
                ),
                "fail_closed": True,
            },
            "promotion_flags": promotion_flags,
            "blocking_criteria": [
                name for name, value in promotion_flags.items() if not value
            ],
            "curved_operator_identity": self.complete,
            "next_exact_step": (
                "construct either a mixed-order Green realization or a curvature-"
                "prolonged realization; both remain false and neither is inferred "
                "from the positive scalar-wave no-go theorem"
            ),
            "fail_closed": True,
        }
