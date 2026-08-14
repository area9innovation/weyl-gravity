from __future__ import annotations

import copy
import unittest

from foundations.check_refined_intersection_cube_v10 import check
from foundations.refine_intersection_cube_v10 import build
from foundations.verify_refined_intersection_cube_v10 import verify


class RefinedIntersectionCubeV10Tests(unittest.TestCase):
    def test_six_decisions_only(self):
        value = build()
        changed = [cell for cell in value["cells"] if "bt_euclidean_revision" in cell]
        self.assertEqual(6, len(changed))
        self.assertEqual(5, sum(item["bt_euclidean_revision"]["evidence_role"] == "DIRECT_LOCAL" for item in changed))

    def test_independent_checker(self):
        self.assertEqual([], check(build())[0])

    def test_unrelated_cell_drift_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if "bt_euclidean_revision" not in item)
        cell["summary"] += " drift"
        self.assertTrue(any("undeclared v9 cell drift" in item for item in check(value)[0]))

    def test_reconstruction_promotion_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if item["obligation"] == "RECONSTRUCTION_LIMITS" and "bt_euclidean_revision" in item)
        cell["status"] = "LOCAL_RESULT"
        self.assertTrue(check(value)[0])

    def test_verifier(self):
        self.assertEqual([], verify()[0])


if __name__ == "__main__":
    unittest.main()
