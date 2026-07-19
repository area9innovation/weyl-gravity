from __future__ import annotations

import copy
import unittest

from jsonschema import ValidationError

from spectral.euclidean.generic_background_physical_hessian_h1_h2_contact_finite_rows import (
    build,
    validate,
)


class PhysicalHessianH1H2ContactFiniteRowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_exact_finite_contact_projection(self) -> None:
        theorem = self.value["finite_contact_theorem"]
        self.assertEqual(theorem["contact_count"], 3)
        self.assertEqual(theorem["quotient_dimension"], 10)
        self.assertEqual(
            theorem["mellin_endpoint_check"],
            {"numerator": 0, "denominator": 1},
        )
        self.assertEqual(len(self.value["projection_rows"]), 33)

    def test_unseen_and_equal_box_regressions(self) -> None:
        self.assertTrue(
            all(
                row["channel_defect_count"] == 0
                for row in self.value["interpolation"]["unseen_ledger"]
            )
        )
        self.assertEqual(
            self.value["equal_box_regression"]["combined_contact_finite_value"],
            {"numerator": 3188, "denominator": 27},
        )

    def test_homogeneity_and_i28_relation(self) -> None:
        for contact_index in range(3):
            block = self.value["projection_rows"][11 * contact_index : 11 * (contact_index + 1)]
            for row in block:
                self.assertTrue(
                    all(
                        sum(term["box_exponents"]) == row["numerator_box_degree"]
                        for term in row["minimal_subtraction_finite_terms"]
                    )
                )
            self.assertEqual([row["carrier_id"] for row in block[7:10]], ["I28"] * 3)

    def test_claim_boundary_is_fail_closed(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["GENERIC_CONTACT_MINIMAL_SUBTRACTION_FINITE_ROWS_COMPUTED"])
        self.assertFalse(flags["FINITE_COUNTERTERM_NORMALIZATION_FIXED"])
        self.assertFalse(flags["RENORMALIZED_PHYSICAL_TRIANGLE_BULK_REDUCED"])
        self.assertFalse(flags["QME_OR_ANOMALY_STATUS_CHANGED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_schema_rejects_triangle_promotion(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["claim_flags"]["RENORMALIZED_PHYSICAL_TRIANGLE_BULK_REDUCED"] = True
        with self.assertRaises(ValidationError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
