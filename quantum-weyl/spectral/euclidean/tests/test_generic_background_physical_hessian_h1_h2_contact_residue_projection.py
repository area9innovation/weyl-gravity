from __future__ import annotations

import copy
import unittest

from jsonschema import ValidationError

from spectral.euclidean.generic_background_physical_hessian_h1_h2_contact_residue_projection import (
    build,
    validate,
)


class PhysicalHessianH1H2ContactResidueProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_exact_generic_contact_projection(self) -> None:
        theorem = self.value["endpoint_theorem"]
        self.assertEqual(theorem["contact_count"], 3)
        self.assertEqual(theorem["endpoint_count"], 6)
        self.assertEqual(theorem["quotient_dimension"], 10)
        self.assertEqual(len(self.value["projection_rows"]), 33)

    def test_unseen_fixtures_and_equal_box_regression(self) -> None:
        unseen = self.value["interpolation"]["unseen_ledger"]
        self.assertEqual(len(unseen), 2)
        self.assertTrue(all(row["channel_defect_count"] == 0 for row in unseen))
        self.assertEqual(
            self.value["equal_box_regression"]["combined_all_contacts"],
            {"numerator": 2704, "denominator": 27},
        )

    def test_homogeneity_and_symmetric_i28_section(self) -> None:
        for contact_index in range(3):
            block = self.value["projection_rows"][11 * contact_index : 11 * (contact_index + 1)]
            for row in block:
                self.assertTrue(
                    all(
                        sum(term["box_exponents"]) == row["numerator_box_degree"]
                        for term in row["single_endpoint_terms"]
                    )
                )
            self.assertEqual([row["carrier_id"] for row in block[7:10]], ["I28"] * 3)
        self.assertTrue(
            self.value["claim_flags"]["SYMMETRIC_I28_QUOTIENT_SECTION_PRESERVED"]
        )

    def test_claim_boundary_remains_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertFalse(flags["RENORMALIZED_GENERIC_MIXED_ROWS_ASSEMBLED"])
        self.assertFalse(flags["PHYSICAL_M14_CORNER_CLASS_DISPOSED"])
        self.assertFalse(flags["QME_OR_ANOMALY_STATUS_CHANGED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_schema_rejects_m14_promotion(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["claim_flags"]["PHYSICAL_M14_CORNER_CLASS_DISPOSED"] = True
        with self.assertRaises(ValidationError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
