from __future__ import annotations

import unittest

from foundations.check_refined_intersection_cube_v12 import check
from foundations.refine_intersection_cube_v12 import build
from foundations.verify_refined_intersection_cube_v12 import REPORT, verify


class RefinedIntersectionCubeV12Tests(unittest.TestCase):
    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_build_passes_independent_checker(self):
        self.assertEqual(check(build())[0], [])

    def test_unrelated_cell_mutation_fails(self):
        value = build()
        value["cells"][0]["summary"] += " drift"
        self.assertTrue(check(value)[0])

    def test_direct_role_mutation_fails(self):
        value = build()
        cell = next(cell for cell in value["cells"] if cell.get("local_weak_wave_revision", {}).get("evidence_role") == "DIRECT_LOCAL")
        cell["evidence_roles"]["FOUNDATIONAL_CODED_LOCAL_WEAK_WAVE_TEST_CLASS_V1"] = "SUPPORTING"
        self.assertTrue(check(value)[0])

    def test_supporting_evidence_cannot_promote_wellposedness(self):
        value = build()
        cell = next(cell for cell in value["cells"] if cell.get("local_weak_wave_revision", {}).get("previous_status") == "PIECES_ONLY")
        cell["status"] = "LOCAL_RESULT"
        self.assertTrue(check(value)[0])

    def test_causal_promotion_fails(self):
        value = build()
        value["claim_flags"]["causal_support_established"] = True
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
