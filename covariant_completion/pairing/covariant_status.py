"""Fail-closed status for the remaining auxiliary-current comparison."""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.symplectic import BranchResidues
from field_bv_identification.polarized_state import PolarizedPairingTransfer


@dataclass(frozen=True)
class CovariantPairingStatus:
    reduced_branch_pairing: bool
    algebraic_bfv_pairing: bool
    auxiliary_green_current_emitted: bool = False
    auxiliary_metric_current_comparison_emitted: bool = False

    @staticmethod
    def build() -> "CovariantPairingStatus":
        BranchResidues().verify()
        PolarizedPairingTransfer.build().verify()
        return CovariantPairingStatus(True, True)

    @property
    def complete(self) -> bool:
        return (
            self.reduced_branch_pairing
            and self.algebraic_bfv_pairing
            and self.auxiliary_green_current_emitted
            and self.auxiliary_metric_current_comparison_emitted
        )

    def certificate(self) -> dict[str, object]:
        return {
            "schema": "pure-weyl-covariant-cauchy-pairing-status-v1",
            "proved": {
                "metric_physical_branch_current": self.reduced_branch_pairing,
                "EAL_Krein_signs": "+E,-A,-L",
                "algebraic_BFV_CE_orientation": self.algebraic_bfv_pairing,
                "centered_Gram": "I_2 in the energy-mode theorem",
            },
            "remaining_for_certificate_D": {
                "auxiliary_differential_green_current": self.auxiliary_green_current_emitted,
                "slab_boundary_current": False,
                "auxiliary_pullback_equals_metric_current_mod_d_and_Q": (
                    self.auxiliary_metric_current_comparison_emitted
                ),
                "covariant_causal_equals_Cauchy_pairing": False,
            },
            "complete_covariant_pairing_certificate": self.complete,
            "guard": (
                "the reduced mode normalization and final I_2 do not by themselves "
                "prove the auxiliary covariant/Cauchy current comparison"
            ),
        }
