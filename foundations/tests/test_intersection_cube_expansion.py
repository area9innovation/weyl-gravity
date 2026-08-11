import copy
import unittest

from foundations.verify_intersection_cube_expansion import CUBE, REPORT, RESULT, load, verify


class IntersectionCubeExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.cube = load(CUBE)
        cls.report = REPORT.read_text()

    def test_expansion(self):
        self.assertEqual([], verify())

    def test_digest_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["cell_additions"][0]["status"] = "PRIORITY_GAP"
        self.assertTrue(verify(result=result))

    def test_cube_drift_fails(self):
        cube = copy.deepcopy(self.cube)
        cube["cells"] = cube["cells"][:-1]
        self.assertTrue(verify(cube=cube))

    def test_literature_completion_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["literature_complete"] = True
        self.assertTrue(verify(result=result))

    def test_report_boundary_fails(self):
        self.assertTrue(verify(report=self.report.replace("not a literature-absence claim", "globally absent")))


if __name__ == "__main__":
    unittest.main()
