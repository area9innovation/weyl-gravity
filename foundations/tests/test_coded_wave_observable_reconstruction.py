from __future__ import annotations

import copy
import json
import unittest

from foundations.verify_coded_wave_observable_reconstruction import REPORT, RESULT, verify


class CodedWaveObservableReconstructionTests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_cutoff_mutation_fails(self):
        value = self.value()
        value["fixtures"][1]["approximants"][2]["cutoff_index"] -= 1
        self.assertTrue(verify(result=value)[0])

    def test_sample_hash_mutation_fails(self):
        value = self.value()
        value["fixtures"][0]["approximants"][0]["sample_sha256"] = "0" * 64
        self.assertTrue(verify(result=value)[0])

    def test_detector_mutation_fails(self):
        value = self.value()
        value["declared_observable"]["test_values"][-1] = [1, 1]
        self.assertTrue(verify(result=value)[0])

    def test_source_state_mutation_fails(self):
        value = self.value()
        value["fixtures"][2]["source_state"]["right"][0] = [4, 1]
        self.assertTrue(verify(result=value)[0])

    def test_uniform_claim_cannot_be_demoted(self):
        value = self.value()
        value["claim_flags"]["uniform_bounded_time_convergence_proved"] = False
        self.assertTrue(verify(result=value)[0])

    def test_causal_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["causal_support_proved"] = True
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
