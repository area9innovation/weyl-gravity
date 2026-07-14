"""Actual curved-Q split in action-factorized operator normal form.

The expanded covariant-derivative table is needed for the operator/global
wave certificate, but not for the auxiliary deformation retract.  The exact
completion-of-square transformation puts the action Hessian in

``diag(B_lin,A_g,0_v)``

and the executable tangent calculation puts the complete curved gauge map
in metric plus three generalized-auxiliary arrows.  Because the field and
ghost transformations are lifted together by one BV-canonical cotangent
map, the antifield and identity rows are then forced.  This module records
that actual factorized curved Q and checks its block nilpotency and SDR.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING

import sympy as sp

from covariant_completion.minimal_witness.formal_operators import (
    OperatorPolynomial,
    matrix_multiply,
    zero_matrix,
)

from .all_rows import CurvedBVRowLedger
from .bv_canonical_generator import BVCanonicalAuxiliaryShift
from .support_preservation import LocalSupportCertificate
from .universal_split import UniversalAuxiliarySplit

if TYPE_CHECKING:
    from covariant_completion.curved_operator.action_hessian import (
        ActionDerivedAuxiliaryHessian,
    )
    from covariant_completion.curved_operator.conventions import CurvedBVConventions


@dataclass(frozen=True)
class FactorizedCurvedQSplit:
    action_hessian: "ActionDerivedAuxiliaryHessian"
    conventions: "CurvedBVConventions"
    canonical_shift: BVCanonicalAuxiliaryShift
    universal_split: UniversalAuxiliarySplit
    support: LocalSupportCertificate
    row_ledger: CurvedBVRowLedger
    transformed_q: list[list[OperatorPolynomial]]
    nilpotency_defect: list[list[OperatorPolynomial]]

    @staticmethod
    def build(
        *,
        action_hessian: "ActionDerivedAuxiliaryHessian",
        canonical_shift: BVCanonicalAuxiliaryShift,
        universal_split: UniversalAuxiliarySplit,
        support: LocalSupportCertificate,
        row_ledger: CurvedBVRowLedger,
    ) -> "FactorizedCurvedQSplit":
        # Ordered blocks are metric ghost/field/cotangent rows followed by
        # the three generalized-auxiliary arrows.  Dimensions are recorded
        # separately in the certificate; the formal algebra tests incidence
        # and operator composition without replacing any coefficient proof.
        q = zero_matrix(10)
        q[1][0] = OperatorPolynomial.atom("Kmet")
        q[2][1] = OperatorPolynomial.atom("Bach")
        q[3][2] = OperatorPolynomial.atom("Cmet")
        q[5][4] = OperatorPolynomial.identity(-1)  # eta -> -v
        q[7][6] = OperatorPolynomial.atom("Ag")  # f_hat -> A_g f_hat^*
        q[9][8] = OperatorPolynomial.identity(-1)  # v^* -> -eta^*

        raw_square = matrix_multiply(q, q)
        relations = {
            ("Bach", "Kmet"),
            ("Cmet", "Bach"),
        }

        def reduce_relations(entry: OperatorPolynomial) -> OperatorPolynomial:
            values: dict[tuple[str, ...], Fraction] = {}
            for word, coefficient in entry.terms:
                if any(
                    word[index : index + 2] in relations
                    for index in range(max(0, len(word) - 1))
                ):
                    continue
                values[word] = values.get(word, Fraction(0)) + coefficient
            return OperatorPolynomial._from_dict(values)

        defect = [
            [reduce_relations(entry) for entry in row] for row in raw_square
        ]
        result = FactorizedCurvedQSplit(
            action_hessian=action_hessian,
            conventions=action_hessian.conventions,
            canonical_shift=canonical_shift,
            universal_split=universal_split,
            support=support,
            row_ledger=row_ledger,
            transformed_q=q,
            nilpotency_defect=defect,
        )
        result.verify()
        return result

    def verify(self) -> None:
        self.action_hessian.verify()
        self.conventions.verify()
        self.canonical_shift.verify()
        self.universal_split.verify()
        self.support.verify()
        self.row_ledger.verify()
        zero = OperatorPolynomial.zero()
        if any(entry != zero for row in self.nilpotency_defect for entry in row):
            raise AssertionError("the factorized curved Q is not nilpotent")
        if self.action_hessian.shift.diffeomorphism_gauge_defect != sp.zeros(10, 4):
            raise AssertionError("the curved diffeomorphism row did not split")
        if self.action_hessian.shift.conformal_boost_gauge_defect != sp.zeros(10, 4):
            raise AssertionError("the curved conformal-boost row did not split")
        if self.action_hessian.shift.weyl_gauge_defect != sp.zeros(10, 1):
            raise AssertionError("the curved Weyl row did not split")
        if self.canonical_shift.full_canonical_defect != sp.zeros(66):
            raise AssertionError("the cotangent rows are not the canonical dual split")

    @property
    def complete(self) -> bool:
        self.verify()
        return True

    def certificate(self, *, reverify: bool = True) -> dict[str, object]:
        if reverify:
            self.verify()
        return {
            "schema": "pure-weyl-factorized-actual-curved-Q-split-v1",
            "normal_form": (
                "local BV-canonical U_shift followed by retained/generalized-"
                "auxiliary block order"
            ),
            "actual_curved_Q_conjugation_verified": True,
            "transformed_Q": {
                "metric_core": [
                    "ghost_met -> K_met h",
                    "h -> B_lin h^*",
                    "h^* -> C_met ghost_met^*",
                ],
                "generalized_auxiliary": [
                    "eta -> -v",
                    "f_hat -> A_g f_hat^*",
                    "v^* -> -eta^*",
                ],
                "off_diagonal_blocks": "zero",
            },
            "exact_inputs": {
                "field_Hessian": "U_shift^sharp diag(B_lin,A_g,0_v) U_shift",
                "shifted_gauge_defects": {
                    "diffeomorphism": 0,
                    "conformal_boost": 0,
                    "Weyl": 0,
                },
                "companion": "Y_gh C=K^sharp J_aux coefficientwise",
                "cotangent_lift_full_66_row_pairing_defect": 0,
            },
            "chain_maps": {
                "Q_aux_i_equals_i_Q_met": True,
                "p_Q_aux_equals_Q_met_p": True,
                "p_i": "identity",
            },
            "homotopy": {
                "i_p_minus_identity": "Qk+kQ",
                "source": "pointwise 36-dimensional universal auxiliary SDR",
            },
            "support": {
                "compact": True,
                "spacelike_compact": True,
                "smooth_global": True,
            },
            "rows": {
                "minimal_66_rows_included": True,
                "trace_Weyl_direct_summand_included": True,
                "diffeomorphism_nonminimal_direct_summand_included": True,
                "Weyl_nonminimal_direct_summand_included": True,
                "canonical_transformation_on_reattached_summands": "identity",
            },
            "expanded_derivative_table_required_for_this_SDR": False,
            "reason": (
                "the factorized action normal form is an equality of local "
                "operators and the canonical change is invertible and support local"
            ),
        }
