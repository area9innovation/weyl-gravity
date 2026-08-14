from __future__ import annotations

import json
import unittest

from foundations.verify_coded_weak_wave_h2_test_completion import REPORT, RESULT, verify


class CodedWeakWaveH2TestCompletionTests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_h2_multiindex_mutation_fails(self):
        value = self.value()
        value["rational_test_codes"]["derivative_multiindices"].pop()
        self.assertTrue(verify(result=value)[0])

    def test_cutoff_mutation_fails(self):
        value = self.value()
        value["fixtures"][1]["binary_cutoff_offsets"]["scalar_wave"] -= 1
        self.assertTrue(verify(result=value)[0])

    def test_modulus_mutation_fails(self):
        value = self.value()
        value["fixtures"][2]["precision_samples"][3]["scalar_wave_squared_error_bound"] = [1, 1]
        self.assertTrue(verify(result=value)[0])

    def test_bare_smooth_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["bare_extensional_smooth_tests_uniformly_named"] = True
        self.assertTrue(verify(result=value)[0])

    def test_distribution_uniqueness_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["uniqueness_among_arbitrary_distributions_proved"] = True
        self.assertTrue(verify(result=value)[0])

    def test_causal_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["strict_causal_support_proved"] = True
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
