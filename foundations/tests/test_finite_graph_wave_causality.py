import copy
import unittest
from foundations.verify_finite_graph_wave_causality import REPORT, RESULT, verify
import json


class FiniteGraphWaveCausalityTests(unittest.TestCase):
    def test_repository_result(self): self.assertEqual([], verify()[0])
    def test_kernel_mutation_fails(self):
        value = json.loads(RESULT.read_text()); value["fixtures"][0]["retarded_kernels"][2][0][0] = [99, 1]
        self.assertTrue(verify(result=value)[0])
    def test_lorentzian_promotion_fails(self):
        value = json.loads(RESULT.read_text()); value["claim_flags"]["lorentzian_causal_claim"] = True
        self.assertTrue(verify(result=value)[0])
    def test_report_drift_fails(self): self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__": unittest.main()
