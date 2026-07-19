from __future__ import annotations

from copy import deepcopy
import json
import unittest

from spectral.euclidean.generic_background_physical_hessian_triangle_master_completeness import (
    OUTPUT,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_triangle_master_completeness import (
    verify,
)


class GenericBackgroundPhysicalHessianTriangleMasterCompletenessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_minimal_rank_ladder(self) -> None:
        self.assertEqual(
            [row["generic_rank"] for row in self.value["rank_ladder"]],
            [47, 48, 49, 50, 51, 52],
        )
        self.assertEqual(self.value["canonical_tangent_pivot_count"], 46)
        self.assertTrue(self.value["claim_flags"]["M14_SINGLET_REQUIRED"])
        self.assertTrue(self.value["claim_flags"]["STANDARD_S3_MASTER_PAIR_REQUIRED"])

    def test_all_physical_rows_are_in_span(self) -> None:
        rows = self.value["physical_channel_rows"]
        self.assertEqual(len(rows), 11)
        self.assertEqual({row["generic_augmented_rank"] for row in rows}, {52})
        self.assertEqual(
            {row["membership_status"] for row in rows},
            {"IN_SIX_MASTER_RELATIVE_IBP_SPAN"},
        )

    def test_fail_closed_master_value_boundary(self) -> None:
        flags = self.value["claim_flags"]
        self.assertFalse(flags["RENORMALIZED_SIX_MASTER_VALUES_COMPUTED"])
        self.assertFalse(flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"])
        self.assertFalse(flags["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"])
        self.assertFalse(flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_rank_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["physical_channel_rows"][0]["generic_augmented_rank"] = 53
        with self.assertRaises(Exception):
            validate(mutant)

    def test_fast_independent_verifier(self) -> None:
        self.assertEqual(verify(self.value), self.value)


if __name__ == "__main__":
    unittest.main()
