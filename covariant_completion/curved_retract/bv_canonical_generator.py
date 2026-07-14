"""BV-canonical cotangent lift of the local curved auxiliary shift.

For a local triangular field transformation ``q_new=F(q_old)``, the type-II
functional ``<q_new^*,F(q_old)>`` defines its cotangent lift.  This remains
true when ``F`` is differential: the old antifields contain the *formal*
adjoint of the Frechet derivative, and compact support removes the boundary
term.  The construction below records the exact pure-Weyl shifts and checks
their already-instantiated Fourier matrices against the BV pairings.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib

import sympy as sp

from covariant_completion.auxiliary_equivalence import GeneralizedAuxiliaryRetract


def _digest(matrix: sp.MatrixBase) -> str:
    return hashlib.sha256(
        sp.srepr(sp.ImmutableDenseMatrix(matrix)).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True)
class BVCanonicalAuxiliaryShift:
    """Canonical-generator and Fourier cotangent-lift certificate."""

    retract: GeneralizedAuxiliaryRetract
    field_canonical_defect: sp.Matrix
    ghost_canonical_defect: sp.Matrix

    @staticmethod
    def build(
        retract: GeneralizedAuxiliaryRetract | None = None,
    ) -> "BVCanonicalAuxiliaryShift":
        if retract is None:
            retract = GeneralizedAuxiliaryRetract.build()
        system = retract.system
        zeta = system.covector
        negative_covector = {component: -component for component in zeta}

        field_change = retract.field_new_to_old
        ghost_change = retract.ghost_new_to_old
        total_change = retract.total_new_to_old
        field_dual_change = total_change[33:57, 33:57]
        ghost_dual_change = total_change[57:66, 57:66]

        field_canonical_defect = sp.simplify(
            field_change.subs(negative_covector).T
            * system.field_fibre_pairing
            * field_dual_change
            - system.field_fibre_pairing
        )
        ghost_canonical_defect = sp.simplify(
            ghost_change.subs(negative_covector).T
            * system.gauge_fixing_pairing
            * ghost_dual_change
            - system.gauge_fixing_pairing
        )
        result = BVCanonicalAuxiliaryShift(
            retract=retract,
            field_canonical_defect=field_canonical_defect,
            ghost_canonical_defect=ghost_canonical_defect,
        )
        result.verify()
        return result

    def verify(self) -> None:
        if self.field_canonical_defect != sp.zeros(24):
            raise AssertionError("the field cotangent lift is not canonical")
        if self.ghost_canonical_defect != sp.zeros(9):
            raise AssertionError("the ghost cotangent lift is not canonical")

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-local-bv-canonical-auxiliary-shift-v1",
            "type_II_generating_functional": (
                "F_shift=int[<h_new^*,h>+<v_new^*,v>+"
                "<phi_hat_new^*,phi-A_g^{-1}G^b(g,b)>+"
                "<eta_new^*,xi_0-d sigma>+<sigma_new^*,sigma>+...]"
            ),
            "new_fields": {
                "phi_hat": "phi-A_g^{-1}G^b(g,b)",
                "eta": "xi_0-d sigma",
            },
            "induced_antifields": {
                "metric_and_vector": (
                    "old cotangents equal new cotangents minus the formal "
                    "Frechet adjoints of D(A_g^{-1}G^b) applied to phi_hat^*"
                ),
                "xi_0_star": "eta_star",
                "sigma_star": "sigma_new_star-d^sharp eta_star (graded convention)",
            },
            "local_BV_cotangent_lift_is_canonical": True,
            "reason": (
                "the transformation is defined by a local type-II generating "
                "functional; its cotangent rows use formal adjoints"
            ),
            "Fourier_regression": {
                "field_pairing_defect": "zero",
                "ghost_pairing_defect": "zero",
                "full_field_dimension": 24,
                "full_ghost_dimension": 9,
                "field_change_sha256": _digest(
                    self.retract.field_new_to_old
                ),
                "ghost_change_sha256": _digest(
                    self.retract.ghost_new_to_old
                ),
            },
            "all_cotangent_rows_generated_together": True,
            "curved_Q_conjugation_verified": False,
            "theorem_boundary": (
                "canonicality of the local shift is exact, but canonicality alone "
                "does not prove that the un-emitted curved Q becomes block split"
            ),
        }
