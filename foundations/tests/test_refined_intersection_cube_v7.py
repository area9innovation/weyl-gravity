from __future__ import annotations

import copy
import unittest

from foundations.check_refined_intersection_cube_v7 import check
from foundations.refine_intersection_cube_v7 import build
from foundations.verify_refined_intersection_cube_v7 import verify


class RefinedIntersectionCubeV7Tests(unittest.TestCase):
    def test_exact_ten_cell_promotion(self):
        value = build()
        revised = [cell for cell in value["cells"] if cell.get("classification_revision", {}).get("certificate") == "FOUNDATIONAL_FINITE_OPERATOR_TEN_CELL_CLOSURE_V1"]
        self.assertEqual(10, len(revised))
        self.assertEqual(9, sum(cell["status"] == "LOCAL_RESULT" for cell in revised))
        self.assertEqual(1, sum(cell["status"] == "PIECES_ONLY" for cell in revised))

    def test_independent_checker(self):
        self.assertEqual([], check(build())[0])

    def test_unrelated_cell_drift_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if "classification_revision" not in item)
        cell["summary"] += " drift"
        self.assertTrue(any("untouched cell drift" in item for item in check(value)[0]))

    def test_renormalization_promotion_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if item["obligation"] == "RENORMALIZED_PRODUCTS" and item.get("classification_revision"))
        cell["status"] = "LOCAL_RESULT"
        self.assertTrue(check(value)[0])

    def test_verifier(self):
        self.assertEqual([], verify()[0])


if __name__ == "__main__":
    unittest.main()
