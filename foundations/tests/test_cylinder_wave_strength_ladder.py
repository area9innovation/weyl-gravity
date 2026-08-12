import copy
import unittest

from foundations.verify_cylinder_wave_strength_ladder import REPORT, RESULT, load, verify


class CylinderWaveStrengthLadderTests(unittest.TestCase):
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

    def test_rca0_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["arbitrary_energy_completion_formalized_in_rca0"] = True
        self.assertTrue(verify(result=result)[0])

    def test_relation_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["typed_relation_graph"]["edges"][0]["to"] = "NO-SUCH-NODE"
        self.assertTrue(verify(result=result)[0])

    def test_literature_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["literature_dependencies"][0]["artifact_status"] = "CONTENT_PINNED"
        self.assertTrue(verify(result=result)[0])

    def test_report_boundary_fails(self):
        report = self.report.replace("no new `LORENTZIAN-CAUSAL`", "a causal theorem")
        self.assertTrue(verify(report=report)[0])


if __name__ == "__main__":
    unittest.main()
