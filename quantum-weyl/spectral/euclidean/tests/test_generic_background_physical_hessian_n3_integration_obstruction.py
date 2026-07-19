from __future__ import annotations

from copy import deepcopy
import json
import unittest

from spectral.euclidean.generic_background_physical_hessian_n3_integration_obstruction import (
    OUTPUT,
    validate,
)
from spectral.euclidean.verify_generic_background_physical_hessian_n3_integration_obstruction import (
    verify,
)


class GenericBackgroundPhysicalHessianN3IntegrationObstructionTests(
    unittest.TestCase
):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_exact_relative_rank_jump_and_dual_witness(self) -> None:
        quotient = self.value["relative_quotient"]
        self.assertEqual(quotient["symmetric_point_relative_IBP_plus_master_rank"], 49)
        self.assertEqual(quotient["M14_augmented_rank"], 50)
        self.assertEqual(quotient["M14_rank_jump"], 1)
        witness = quotient["M14_dual_nonmembership_witness"]
        self.assertEqual(
            witness["witness_type"],
            "COMPLETE_NONMEMBERSHIP_WITNESS_IN_DECLARED_SYMMETRIC_POINT_POLE4_AMBIENT",
        )
        self.assertEqual(witness["ambient_alpha_monomial_count"], 55)
        self.assertEqual(witness["relative_span_annihilation"], "ZERO")
        self.assertEqual(witness["M14_normalization"], {"numerator": 1, "denominator": 1})

    def test_logarithmic_corner_and_channel_ledger(self) -> None:
        corner = self.value["corner_asymptotic"]
        self.assertEqual(corner["angular_integral_per_corner"], {"numerator": 1, "denominator": 6})
        self.assertEqual(corner["corner_count"], 3)
        self.assertEqual(
            corner["total_log_1_over_epsilon_coefficient"],
            {"numerator": 1, "denominator": 2},
        )
        nonzero = [
            row["channel_id"]
            for row in self.value["channel_rows"]
            if row["obstruction_status"] == "NONZERO"
        ]
        self.assertEqual(nonzero, self.value["nonzero_obstruction_channels"])
        self.assertEqual(len(nonzero), 8)

    def test_fail_closed_completion_boundary(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["PHYSICAL_H1_ONLY_SYMMETRIC_POINT_INTEGRATION_OBSTRUCTED"])
        self.assertTrue(flags["LOGARITHMIC_SIMPLEX_CORNER_CLASS_IDENTIFIED"])
        self.assertFalse(flags["CURVATURE_SQUARED_H2_IMPORTED"])
        self.assertFalse(flags["H2_CANCELLATION_OF_CORNER_CLASS_PROVED"])
        self.assertFalse(flags["RENORMALIZED_SUBTRACTION_PRESCRIPTION_FIXED"])
        self.assertFalse(flags["PHYSICAL_N3_TRIANGLE_INTEGRATED"])
        self.assertFalse(flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_formula_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["channel_rows"][0]["M14_e3_over_e2_power4_coefficient"]["numerator"] += 1
        with self.assertRaises(Exception):
            validate(mutant)

    def test_rank_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["relative_quotient"]["M14_augmented_rank"] = 49
        with self.assertRaises(Exception):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(self.value), self.value)


if __name__ == "__main__":
    unittest.main()
