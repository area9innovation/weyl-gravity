import copy
import unittest

from foundations.verify_refined_intersection_cube_v2 import REPORT, RESULT, load, verify


class RefinedIntersectionCubeV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.report = REPORT.read_text()

    def test_repository_result(self):
        self.assertEqual([], verify()[0])

    def test_digest_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["independent_checker"]["expected_digest"] = "0" * 64
        self.assertTrue(verify(result=result)[0])

    def test_no_transfer_coverage_promotion_fails(self):
        result = copy.deepcopy(self.result)
        cell = next(x for x in result["cells"] if x["migration_status"] == "REVIEWED_NO_TRANSFER")
        cell["status"] = "LITERATURE_RESULT"
        self.assertTrue(verify(result=result)[0])

    def test_pending_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["dimensions"]["migration_pending_cells"] = 1
        self.assertTrue(verify(result=result)[0])

    def test_report_interpretation_fails(self):
        report = self.report.replace("does not answer whether other literature supports the cell", "proves no other literature supports the cell")
        self.assertTrue(verify(report=report)[0])


if __name__ == "__main__":
    unittest.main()
