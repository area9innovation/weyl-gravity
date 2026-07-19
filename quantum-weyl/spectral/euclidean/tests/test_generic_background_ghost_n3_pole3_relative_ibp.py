from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.generic_background_ghost_n3_pole3_relative_ibp import (
    OUTPUT,
    SCHEMA,
    validate,
)
from spectral.euclidean.verify_generic_background_ghost_n3_pole3_relative_ibp import (
    verify,
)


class GenericGhostN3PoleThreeRelativeIBPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_independent_fast_exact_fixture_verifier(self) -> None:
        verify(exhaustive=False)

    def test_rank_and_claim_boundary(self) -> None:
        ranks = self.value["rank_ledger"]
        self.assertEqual(ranks["open_edge_tangent_rank"], 27)
        self.assertEqual(ranks["open_edge_tangent_plus_master_rank"], 30)
        self.assertEqual(
            ranks["open_edge_tangent_plus_master_and_targets_rank"], 30
        )
        self.assertEqual(ranks["corner_zero_tangent_plus_master_rank"], 26)
        self.assertTrue(
            all(row["augmented_rank"] == 27 for row in ranks["corner_zero_augmented_ranks"])
        )
        self.assertTrue(
            self.value["claim_flags"][
                "TEN_POLE3_ROWS_REDUCED_TO_J_AND_TWO_DERIVATIVE_MASTERS"
            ]
        )
        self.assertFalse(self.value["claim_flags"]["I29_POLE4_REDUCED"])
        self.assertFalse(
            self.value["claim_flags"]["GENERIC_GHOST_N3_FULL_KINEMATIC_FUNCTIONS_COMPUTED"]
        )

    def test_four_normalized_corner_nonmembership_witnesses(self) -> None:
        witnesses = self.value["corner_zero_dual_witnesses"]
        self.assertEqual(
            set(witnesses), {"I10_123", "I24_123", "I25_123", "I28_123"}
        )
        for witness in witnesses.values():
            self.assertEqual(witness["target_normalization"], "ONE")
            self.assertTrue(witness["annihilates_corner_zero_span"])
            self.assertEqual(witness["generic_base_rank"], 26)
            self.assertEqual(witness["fixture_base_rank"], 26)

    def test_schema_rejects_promotion(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["CORNER_LOG_BUBBLE_SYSTEM_EVALUATED"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutant)

    def test_formula_digest_rejects_mutation(self) -> None:
        mutant = deepcopy(self.value)
        mutant["channel_rows"][0]["master_coordinates"]["J_triangle"][
            "numerator_terms"
        ][0]["coefficient"]["numerator"] += 1
        with self.assertRaises(ValueError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
