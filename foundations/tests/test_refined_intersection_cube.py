import copy
import unittest

from foundations.verify_refined_intersection_cube import REPORT, RESULT, load, verify


class RefinedIntersectionCubeTests(unittest.TestCase):
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

    def test_blind_inheritance_fails(self):
        result = copy.deepcopy(self.result)
        cell = next(x for x in result["cells"] if x["parent_obligation"] == "STATES_PROBABILITY")
        cell["migration_relation"] = "EXACT_ONE_TO_ONE"
        self.assertTrue(verify(result=result)[0])

    def test_qme_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["all_576_cells_assessed"] = True
        self.assertTrue(verify(result=result)[0])

    def test_report_semantic_boundary_fails(self):
        report = self.report.replace("Finite interaction is no longer finite renormalization", "Finite interaction implies finite renormalization")
        self.assertTrue(verify(report=report)[0])


if __name__ == "__main__":
    unittest.main()
