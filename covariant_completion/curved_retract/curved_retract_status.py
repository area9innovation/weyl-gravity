"""Fail-closed aggregate for the curved auxiliary deformation retract."""

from __future__ import annotations

from dataclasses import dataclass

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract

from .auxiliary_eom_shift import CurvedAuxiliaryEOMShift
from .bv_canonical_generator import BVCanonicalAuxiliaryShift
from .support_preservation import LocalSupportCertificate
from .universal_split import UniversalAuxiliarySplit


@dataclass(frozen=True)
class CurvedRetractStatus:
    auxiliary_shift: CurvedAuxiliaryEOMShift
    canonical_shift: BVCanonicalAuxiliaryShift
    universal_split: UniversalAuxiliarySplit
    support: LocalSupportCertificate
    curved_i_is_chain_map: bool = False
    curved_p_is_chain_map: bool = False
    curved_ip_homotopy_identity: bool = False
    actual_curved_Q_conjugation_verified: bool = False
    all_full_BV_rows_reconstructed: bool = False

    @staticmethod
    def build() -> "CurvedRetractStatus":
        retract = GeneralizedAuxiliaryRetract.build()
        result = CurvedRetractStatus(
            auxiliary_shift=CurvedAuxiliaryEOMShift.build(),
            canonical_shift=BVCanonicalAuxiliaryShift.build(retract),
            universal_split=UniversalAuxiliarySplit.build(retract),
            support=LocalSupportCertificate.build(),
        )
        result.verify()
        return result

    @property
    def complete(self) -> bool:
        return all(
            (
                self.curved_i_is_chain_map,
                self.curved_p_is_chain_map,
                self.curved_ip_homotopy_identity,
                self.actual_curved_Q_conjugation_verified,
                self.all_full_BV_rows_reconstructed,
            )
        )

    def verify(self) -> None:
        self.auxiliary_shift.verify()
        self.canonical_shift.verify()
        self.universal_split.verify()
        self.support.verify()
        if self.complete:
            raise AssertionError(
                "curved retract was promoted without the curved Q coefficient table"
            )

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-curved-deformation-retract-status-v1",
            "proved": {
                "exact_nonlinear_auxiliary_completion_of_square": True,
                "pointwise_auxiliary_mass_inverse": True,
                "local_tangent_auxiliary_shift": True,
                "local_shift_has_BV_canonical_cotangent_lift": True,
                "universal_post_shift_36_dimensional_SDR": True,
                "support_preserved_in_all_three_categories": True,
                "p_i_for_displayed_triangular_maps": "identity",
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
            "remaining": [
                "emit the complete curved four-row Q coefficient table",
                "conjugate that Q by the tangent canonical transformation",
                "verify both curved chain maps and ip-1=Qk+kQ componentwise",
                "reattach and check every trace and nonminimal curved row",
            ],
            "curved_deformation_retract": self.complete,
            "guard": (
                "the exact curved action shift, canonical cotangent lift, universal "
                "contractible summand, and support theorem do not by themselves "
                "identify the actual curved Q with the split model"
            ),
        }
