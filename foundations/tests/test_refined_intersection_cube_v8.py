from __future__ import annotations

import copy
import unittest

from foundations.check_refined_intersection_cube_v8 import check
from foundations.refine_intersection_cube_v8 import build
from foundations.verify_refined_intersection_cube_v8 import verify


class RefinedIntersectionCubeV8Tests(unittest.TestCase):
    def test_exact_twenty_cell_promotion(self):
        value = build()
        revised = [cell for cell in value["cells"] if cell.get("classification_revision", {}).get("certificate") == "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1"]
        self.assertEqual(20, len(revised))
        self.assertEqual((17, 3), (sum(cell["status"] == "LOCAL_RESULT" for cell in revised), sum(cell["status"] == "PIECES_ONLY" for cell in revised)))

    def test_independent_checker(self):
        self.assertEqual([], check(build())[0])

    def test_unrelated_cell_drift_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if item.get("classification_revision", {}).get("certificate") != "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1")
        cell["summary"] += " drift"
        self.assertTrue(any("untouched cell drift" in item for item in check(value)[0]))

    def test_product_promotion_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if item["obligation"] == "RENORMALIZED_PRODUCTS" and item.get("classification_revision", {}).get("certificate") == "FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1")
        cell["status"] = "LOCAL_RESULT"
        self.assertTrue(check(value)[0])

    def test_verifier(self):
        self.assertEqual([], verify()[0])


if __name__ == "__main__":
    unittest.main()
