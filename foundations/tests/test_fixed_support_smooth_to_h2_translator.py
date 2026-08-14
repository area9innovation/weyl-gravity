from __future__ import annotations

import json
import unittest

from foundations.verify_fixed_support_smooth_to_h2_translator import REPORT, RESULT, verify


class FixedSupportSmoothToH2TranslatorTests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_cutoff_bound_mutation_fails(self):
        value = self.value()
        value["fixtures"][0]["cutoff_second_derivative_bound"] = [1, 1]
        self.assertTrue(verify(result=value)[0])

    def test_shift_mutation_fails(self):
        value = self.value()
        value["fixtures"][1]["index_shift"] -= 1
        self.assertTrue(verify(result=value)[0])

    def test_modulus_mutation_fails(self):
        value = self.value()
        value["fixtures"][2]["precision_samples"][4]["h2_squared_error_bound"] = [1, 1]
        self.assertTrue(verify(result=value)[0])

    def test_choice_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["choice_principle_used"] = True
        self.assertTrue(verify(result=value)[0])

    def test_bare_function_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["bare_extensional_smooth_function_uniformly_named"] = True
        self.assertTrue(verify(result=value)[0])

    def test_lf_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["full_lf_topology_identified"] = True
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
