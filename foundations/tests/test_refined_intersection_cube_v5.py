from __future__ import annotations

import copy
import unittest

from foundations.check_refined_intersection_cube_v5 import TARGET, check
from foundations.refine_intersection_cube_v5 import build
from foundations.verify_refined_intersection_cube_v5 import verify


class RefinedIntersectionCubeV5Tests(unittest.TestCase):
    def test_one_interface_promotes_probability_target(self):
        value = build()
        cells = {"|".join(cell[key] for key in ("foundation", "carrier", "obligation")): cell for cell in value["cells"]}
        self.assertEqual(cells[TARGET]["status"], "LOCAL_RESULT")
        self.assertEqual(cells[TARGET]["interface_revision"]["relation"], "CONDITIONAL_BRIDGE")
        self.assertEqual(value["dimensions"]["certified_cross_cell_interfaces"], 1)

    def test_independent_checker(self):
        self.assertEqual(check(build())[0], [])

    def test_unrelated_cell_drift_fails(self):
        value = copy.deepcopy(build())
        cell = next(item for item in value["cells"] if "|".join(item[key] for key in ("foundation", "carrier", "obligation")) not in ("CLASSICAL_STANDARD|ALGEBRAIC_CSTAR|STATE_REPRESENTATION", TARGET))
        cell["summary"] += " drift"
        self.assertTrue(any("untouched cell drift" in item for item in check(value)[0]))

    def test_verifier(self):
        self.assertEqual(verify()[0], [])


if __name__ == "__main__":
    unittest.main()
