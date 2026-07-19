from __future__ import annotations

import copy
import unittest

from jsonschema import ValidationError

from spectral.euclidean.generic_background_physical_hessian_symmetric_mixed_boundary_incidence import build, validate


class SymmetricMixedBoundaryIncidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_exact_reconstruction(self) -> None:
        row = self.value["equal_box_tensor_reconstruction"]
        self.assertEqual(row["triangle_full_log_coefficient"], {"numerator": -1975, "denominator": 72})
        self.assertEqual(row["contact_full_log_coefficient"], {"numerator": 2704, "denominator": 27})
        self.assertEqual(row["combined_log_mu2_coefficient"], {"numerator": 15707, "denominator": 216})

    def test_channel_rows_and_i28_section(self) -> None:
        self.assertEqual(len(self.value["channel_rows"]), 11)
        self.assertTrue(all(row["combined_log_mu2_coefficient"] == {"numerator": 0, "denominator": 1} for row in self.value["channel_rows"][7:10]))

    def test_scoped_m14_disposition(self) -> None:
        disposition = self.value["M14_disposition"]
        self.assertEqual(disposition["symmetric_point_algebraic_H2_cancellation"], "REFUTED")
        self.assertEqual(disposition["generic_box_disposition"], "NOT_COMPUTED")
        self.assertFalse(self.value["claim_flags"]["GENERIC_PHYSICAL_M14_DISPOSED"])

    def test_schema_rejects_generic_promotion(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["claim_flags"]["GENERIC_PHYSICAL_M14_DISPOSED"] = True
        with self.assertRaises(ValidationError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
