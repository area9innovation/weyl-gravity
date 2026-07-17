from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_retained_46_stf2_subprincipal_branch_anchor_or_obstruction import (
    build,
    validate,
)
from d_quotient_classical.backreacted_clock.verify_berger_retained_46_stf2_subprincipal_branch_anchor_or_obstruction import (
    verify,
)


class Retained46STF2SubprincipalBranchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_exact_obstruction_replays_independently(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())
        self.assertEqual(
            self.value["filtered_lift_problem"]["rank_ledger"],
            {"allowed_boundary": 4, "plus_augmented": 5, "cross_augmented": 4, "both_augmented": 5},
        )

    def test_normalized_left_null_witness(self) -> None:
        witness = self.value["normalized_obstruction"]
        self.assertEqual(witness["fixture_obstruction_value"], "31/5")
        self.assertEqual(witness["normalized_evaluation_on_physical_columns"], [["1", "0"]])
        self.assertEqual(witness["cross_physical_equation_coefficient"], "71/40")

    def test_scoped_negative_verdict(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["RANK46_PHYSICAL_FILTERED_LIFT_OBSTRUCTED"])
        self.assertFalse(flags["RANK46_SUPPORT_LOCAL_BRANCH_PROJECTOR_ACCEPTED"])
        self.assertFalse(flags["GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO"])
        self.assertFalse(flags["ELL3_BRANCH_MIXING_AUTHORIZED"])
        self.assertFalse(self.value["carrier_consequence"]["global_covariant_enlargement_rank_certified"])

    def test_overclaim_mutations_fail(self) -> None:
        for flag in (
            "SUBPRINCIPAL_BRANCH_ANCHOR_AVAILABLE",
            "RANK46_SUPPORT_LOCAL_BRANCH_PROJECTOR_ACCEPTED",
            "GLOBAL_ALL_CARRIER_PROJECTOR_NO_GO",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)

    def test_witness_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["normalized_obstruction"]["normalized_evaluation_on_physical_columns"] = [["0", "0"]]
        with self.assertRaisesRegex(ValueError, "witness"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
