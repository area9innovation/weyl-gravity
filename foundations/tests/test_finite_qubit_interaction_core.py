import copy
import unittest

from foundations.verify_finite_qubit_interaction_core import RESULT, REPORT, load, verify


class FiniteQubitInteractionCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.report = REPORT.read_text()

    def test_certificate(self):
        self.assertEqual([], verify())

    def test_digest_mutation_fails(self):
        result = copy.deepcopy(self.result)
        result["independent_checker"]["expected_digest"] = "0" * 64
        self.assertTrue(verify(result=result))

    def test_claim_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["qme_restored"] = True
        self.assertTrue(verify(result=result))

    def test_report_boundary_fails_closed(self):
        self.assertTrue(verify(report=self.report.replace("no continuum limit", "continuum available")))


if __name__ == "__main__":
    unittest.main()
