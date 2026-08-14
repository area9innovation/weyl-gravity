from __future__ import annotations

import copy
import json
import unittest

from foundations.check_refined_intersection_cube_v11 import check
from foundations.refine_intersection_cube_v11 import build
from foundations.verify_refined_intersection_cube_v11 import REPORT, verify


class RefinedIntersectionCubeV11Tests(unittest.TestCase):
    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_build_passes_independent_checker(self):
        self.assertEqual(check(build())[0], [])

    def test_unrelated_cell_mutation_fails(self):
        value = build()
        value["cells"][0]["summary"] += " drift"
        self.assertTrue(check(value)[0])

    def test_reconstruction_role_mutation_fails(self):
        value = build()
        cell = next(cell for cell in value["cells"] if cell.get("observable_reconstruction_revision"))
        cell["evidence_roles"]["FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1"] = "SUPPORTING"
        self.assertTrue(check(value)[0])

    def test_causal_promotion_fails(self):
        value = build()
        value["claim_flags"]["causal_support_established"] = True
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
