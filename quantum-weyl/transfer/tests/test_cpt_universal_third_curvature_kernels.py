from __future__ import annotations

from copy import deepcopy
import unittest

from transfer.cpt_universal_third_curvature_kernels import build, validate
from transfer.verify_cpt_universal_third_curvature_kernels import verify


class CptUniversalThirdCurvatureKernelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_five_exact_source_kernels_are_imported(self) -> None:
        rows = self.value["universal_kernels"]
        self.assertEqual([row["carrier_id"] for row in rows], ["I10", "I24", "I25", "I28", "I29"])
        self.assertTrue(all(row["kernel_status"] == "EXACT_UNIVERSAL_MINIMAL_LAPLACE_KERNEL_IMPORTED" for row in rows))

    def test_stabilizer_and_homogeneity_ledger(self) -> None:
        rows = self.value["universal_kernels"]
        self.assertEqual([row["stabilizer_order"] for row in rows], [6, 2, 2, 2, 3])
        self.assertEqual([row["gamma_box_homogeneity"] for row in rows], [-1, -2, -2, -3, -4])

    def test_rank_one_scalar_fixture_is_coefficient_bearing(self) -> None:
        fixture = self.value["source_fixture"]
        self.assertEqual(fixture["bundle_rank"], 1)
        self.assertEqual(fixture["status"], "COEFFICIENT_COMPUTED")

    def test_repository_promotion_is_exactly_refused(self) -> None:
        self.assertEqual(
            self.value["repository_matching_audit"]["verdict"],
            "NO_REPOSITORY_FORM_FACTOR_COEFFICIENT_CAN_BE_INFERRED_FROM_THE_CURRENT_SPECIAL_BACKGROUND_LEDGER",
        )
        self.assertFalse(self.value["claim_flags"]["REPOSITORY_CUBIC_FORM_FACTOR_FUNCTIONS_COMPUTED"])
        self.assertFalse(self.value["claim_flags"]["REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED"])

    def test_coefficient_promotion_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED"] = True
        with self.assertRaises(Exception):
            validate(mutant)

    def test_formula_mutation_is_rejected_by_independent_verifier(self) -> None:
        mutant = deepcopy(self.value)
        mutant["universal_kernels"][2]["raw_log_term"] = "-L12/(15*d3)"
        with self.assertRaises(Exception):
            verify(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.value)


if __name__ == "__main__":
    unittest.main()
