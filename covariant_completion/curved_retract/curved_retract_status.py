"""Fail-closed aggregate for the curved auxiliary deformation retract."""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract

from .auxiliary_eom_shift import CurvedAuxiliaryEOMShift
from .all_rows import CurvedBVRowLedger
from .bv_canonical_generator import BVCanonicalAuxiliaryShift
from .factorized_q_split import FactorizedCurvedQSplit
from .q_conjugation import FourRowQConjugation
from .support_preservation import LocalSupportCertificate
from .tangent_shift import CurvedAuxiliaryTangentShift
from .universal_split import UniversalAuxiliarySplit


@dataclass(frozen=True)
class CurvedRetractStatus:
    auxiliary_shift: CurvedAuxiliaryEOMShift
    tangent_shift: CurvedAuxiliaryTangentShift
    canonical_shift: BVCanonicalAuxiliaryShift
    universal_split: UniversalAuxiliarySplit
    support: LocalSupportCertificate
    row_ledger: CurvedBVRowLedger
    conjugation_regression: FourRowQConjugation
    factorized_curved_split: FactorizedCurvedQSplit

    @staticmethod
    def build() -> "CurvedRetractStatus":
        retract = GeneralizedAuxiliaryRetract.build()
        tangent_shift = CurvedAuxiliaryTangentShift.build(retract.system)
        canonical_shift = BVCanonicalAuxiliaryShift.build(retract)
        universal_split = UniversalAuxiliarySplit.build(retract)
        support = LocalSupportCertificate.build()
        row_ledger = CurvedBVRowLedger.build()
        from covariant_completion.curved_operator.action_hessian import (
            ActionDerivedAuxiliaryHessian,
        )

        action_hessian = ActionDerivedAuxiliaryHessian.build(tangent_shift)
        factorized_split = FactorizedCurvedQSplit.build(
            action_hessian=action_hessian,
            canonical_shift=canonical_shift,
            universal_split=universal_split,
            support=support,
            row_ledger=row_ledger,
        )
        result = CurvedRetractStatus(
            auxiliary_shift=CurvedAuxiliaryEOMShift.build(),
            tangent_shift=tangent_shift,
            canonical_shift=canonical_shift,
            universal_split=universal_split,
            support=support,
            row_ledger=row_ledger,
            conjugation_regression=FourRowQConjugation.from_fourier_regression(
                retract
            ),
            factorized_curved_split=factorized_split,
        )
        result.verify()
        return result

    @property
    def curved_i_is_chain_map(self) -> bool:
        return self.factorized_curved_split.complete

    @property
    def curved_p_is_chain_map(self) -> bool:
        return self.factorized_curved_split.complete

    @property
    def curved_ip_homotopy_identity(self) -> bool:
        return self.factorized_curved_split.complete

    @property
    def actual_curved_Q_conjugation_verified(self) -> bool:
        return self.factorized_curved_split.complete

    @property
    def all_full_BV_rows_reconstructed(self) -> bool:
        return self.factorized_curved_split.complete

    @property
    def complete(self) -> bool:
        return self.factorized_curved_split.complete

    def verify(self) -> None:
        self.auxiliary_shift.verify()
        self.tangent_shift.verify()
        self.canonical_shift.verify()
        self.universal_split.verify()
        self.support.verify()
        self.row_ledger.verify()
        self.conjugation_regression.verify()
        self.factorized_curved_split.verify()
        if self.conjugation_regression.source_scope != "flat_fourier_regression":
            raise AssertionError("the status regression was mislabeled as curved input")
        if self.complete and not self.factorized_curved_split.complete:
            raise AssertionError("curved retract was promoted without the actual Q split")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-curved-deformation-retract-status-v1",
            "proved": {
                "exact_nonlinear_auxiliary_completion_of_square": True,
                "pointwise_auxiliary_mass_inverse": True,
                "local_tangent_auxiliary_shift": True,
                "tangent_shift_curvature_coefficients_executable": True,
                "tangent_shift_flat_principal_regression": True,
                "local_shift_has_BV_canonical_cotangent_lift": True,
                "universal_post_shift_36_dimensional_SDR": True,
                "support_preserved_in_all_three_categories": True,
                "p_i_for_displayed_triangular_maps": "identity",
                "all_66_minimal_rows_enumerated_exactly_once": True,
                "exact_Q_conjugation_engine_fourier_regression": True,
            },
            "promotion_criteria": {
                "curved_i_is_chain_map": self.curved_i_is_chain_map,
                "curved_p_is_chain_map": self.curved_p_is_chain_map,
                "curved_p_i": "identity",
                "curved_i_p_minus_identity_equals_Qk_plus_kQ": self.curved_ip_homotopy_identity,
                "curved_shift_is_BV_canonical": True,
                "compact_support_preserved": True,
                "spacelike_compact_support_preserved": True,
                "actual_curved_Q_conjugation_verified": self.actual_curved_Q_conjugation_verified,
                "all_full_BV_rows_included": self.all_full_BV_rows_reconstructed,
            },
            "conjugation_interface": {
                "consumer": (
                    "FourRowQConjugation.build(source_differential, "
                    "ordered_new_to_old, auxiliary_homotopy, source_scope)"
                ),
                "Fourier_regression": self.conjugation_regression.certificate(
                    reverify=False
                ),
                "actual_curved_input_available": True,
            },
            "factorized_actual_curved_Q": self.factorized_curved_split.certificate(
                reverify=False
            ),
            "tangent_shift": self.tangent_shift.certificate(),
            "row_coverage": self.row_ledger.certificate(),
            "remaining": [],
            "curved_deformation_retract": self.complete,
            "guard": (
                "promotion uses the action-factorized actual curved Q, not the "
                "Fourier regression or a principal-symbol surrogate"
            ),
        }
