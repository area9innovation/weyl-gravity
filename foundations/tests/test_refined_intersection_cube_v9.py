from __future__ import annotations

import copy
import unittest

from foundations.check_refined_intersection_cube_v9 import check
from foundations.refine_intersection_cube_v9 import build
from foundations.verify_refined_intersection_cube_v9 import verify


class RefinedIntersectionCubeV9Tests(unittest.TestCase):
    def test_full_surface_and_review_partition(self):
        value = build()
        revised = [cell for cell in value["cells"] if cell.get("classification_revision", {}).get("certificate") == "FOUNDATIONAL_FULL_SURFACE_GAP_AUDIT_V1"]
        self.assertEqual(576, len(value["cells"]))
        self.assertEqual(175, len(revised))
        self.assertEqual(51, sum(cell["classification_revision"]["previous_status"] == "NOT_MAPPED" for cell in revised))
        self.assertEqual(124, sum(cell["classification_revision"]["previous_status"] == "NOT_EMITTED" for cell in revised))
        self.assertFalse(any(cell["status"] == "NOT_MAPPED" for cell in value["cells"]))

    def test_independent_checker(self):
        self.assertEqual([], check(build())[0])

    def test_missing_coordinate_fails(self):
        value = copy.deepcopy(build())
        value["cells"].pop()
        self.assertTrue(any("Cartesian" in item for item in check(value)[0]))

    def test_prior_result_drift_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if item["status"] == "LOCAL_RESULT")
        cell["summary"] += " drift"
        self.assertTrue(any("prior classified cell drift" in item for item in check(value)[0]))

    def test_reviewed_gap_promotion_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if item["status"] == "REVIEWED_GAP")
        cell["status"] = "LOCAL_RESULT"
        self.assertTrue(check(value)[0])

    def test_verifier(self):
        self.assertEqual([], verify()[0])


if __name__ == "__main__":
    unittest.main()
