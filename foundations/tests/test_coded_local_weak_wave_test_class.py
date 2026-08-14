from __future__ import annotations

import json
import unittest

from foundations.verify_coded_local_weak_wave_test_class import REPORT, RESULT, verify


class CodedLocalWeakWaveTestClassTests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_partition_mutation_fails(self):
        value = self.value()
        value["carrier"]["common_partition"][1] = [1, 7]
        self.assertTrue(verify(result=value)[0])

    def test_rank_mutation_fails(self):
        value = self.value()
        value["separation"]["rank"] = 9
        self.assertTrue(verify(result=value)[0])

    def test_pairing_mutation_fails(self):
        value = self.value()
        value["fixtures"][2]["measurements"][4]["pairing"] = [99, 1]
        self.assertTrue(verify(result=value)[0])

    def test_transport_residual_mutation_fails(self):
        value = self.value()
        value["fixtures"][0]["measurements"][0]["right_transport_residual"] = [1, 100]
        self.assertTrue(verify(result=value)[0])

    def test_all_smooth_tests_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["all_smooth_tests_covered"] = True
        self.assertTrue(verify(result=value)[0])

    def test_causal_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["strict_causal_support_proved"] = True
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
