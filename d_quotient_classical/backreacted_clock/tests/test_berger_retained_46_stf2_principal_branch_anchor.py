from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_retained_46_stf2_principal_branch_anchor import (
    build,
    validate,
)
from d_quotient_classical.backreacted_clock.verify_berger_retained_46_stf2_principal_branch_anchor import (
    verify,
)


class Retained46STF2PrincipalBranchAnchorTests(unittest.TestCase):
    def test_exact_principal_anchor_verdict(self) -> None:
        value = build()
        validate(value)
        self.assertEqual(value, verify())
        self.assertEqual(
            value["idempotent_audit"]["solutions_a_b"],
            [["0", "0"], ["1", "0"]],
        )
        self.assertEqual(
            value["normalized_obstruction_witness"]["normalized_evaluation"],
            "1",
        )

    def test_trivial_and_auxiliary_anchors_are_forbidden(self) -> None:
        anchors = build()["idempotent_audit"]["forbidden_false_anchors"]
        self.assertEqual(len(anchors), 3)
        self.assertTrue(any("contractible STF2" in item for item in anchors))

    def test_full_lower_order_projector_is_not_ruled_out(self) -> None:
        value = build()
        self.assertFalse(
            value["scientific_disposition"]["full_rank_46_lower_order_projector_ruled_out"]
        )
        self.assertFalse(value["claim_flags"]["FULL_RANK_46_PROJECTOR_OBSTRUCTED"])
        self.assertTrue(value["claim_flags"]["SUBPRINCIPAL_ANCHOR_REQUIRED"])

    def test_overclaim_mutations_fail(self) -> None:
        for flag in (
            "PRINCIPAL_DIRECT_SUM_BRANCH_ANCHOR_ACCEPTED",
            "FULL_RANK_46_PROJECTOR_OBSTRUCTED",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
        ):
            mutant = deepcopy(build())
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)


if __name__ == "__main__":
    unittest.main()
