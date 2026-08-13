from __future__ import annotations

import copy
import unittest

from foundations.check_refined_intersection_cube_v6 import SOURCE, TARGET, check
from foundations.refine_intersection_cube_v6 import build
from foundations.verify_refined_intersection_cube_v6 import verify


class RefinedIntersectionCubeV6Tests(unittest.TestCase):
    def test_second_interface_overlays_without_grade_promotion(self):
        value = build()
        cells = {"|".join(cell[key] for key in ("foundation", "carrier", "obligation")): cell for cell in value["cells"]}
        self.assertEqual(cells[SOURCE]["status"], "LOCAL_RESULT")
        self.assertEqual(cells[TARGET]["status"], "LOCAL_RESULT")
        self.assertFalse(cells[TARGET]["interface_revision"]["status_change"])
        self.assertEqual([item["id"] for item in value["certified_interfaces"]], ["STATE_TO_PROBABILITY", "SELECTION_TO_DYNAMICS"])

    def test_independent_checker(self):
        self.assertEqual(check(build())[0], [])

    def test_unrelated_cell_drift_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if "|".join(item[key] for key in ("foundation", "carrier", "obligation")) not in (SOURCE, TARGET))
        cell["summary"] += " drift"
        self.assertTrue(any("untouched cell drift" in item for item in check(value)[0]))

    def test_verifier(self):
        self.assertEqual(verify()[0], [])


if __name__ == "__main__":
    unittest.main()
