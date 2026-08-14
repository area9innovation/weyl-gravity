from __future__ import annotations

import json
import unittest

from foundations.verify_lorentzian_weyl_bv_completion_atlas import REPORT, RESULT, verify


class LorentzianWeylBVCompletionAtlasTests(unittest.TestCase):
    def value(self) -> dict:
        return json.loads(RESULT.read_text())

    def test_repository_result(self):
        self.assertEqual(verify()[0], [])

    def test_strict_causal_erasure_fails(self):
        value = self.value()
        value["branches"][0]["stages"][2]["status"] = "FAIL_CLOSED"
        self.assertTrue(verify(result=value)[0])

    def test_strict_qme_promotion_fails(self):
        value = self.value()
        value["branches"][0]["stages"][8]["status"] = "CERTIFIED"
        self.assertTrue(verify(result=value)[0])

    def test_berger_hadamard_promotion_fails(self):
        value = self.value()
        value["branches"][3]["stages"][5]["status"] = "CERTIFIED"
        self.assertTrue(verify(result=value)[0])

    def test_reduced_mode_promotion_fails(self):
        value = self.value()
        value["branches"][4]["stages"][1]["status"] = "CERTIFIED"
        self.assertTrue(verify(result=value)[0])

    def test_tau_obstruction_erasure_fails(self):
        value = self.value()
        value["branches"][5]["stages"][2]["status"] = "CERTIFIED"
        self.assertTrue(verify(result=value)[0])

    def test_full_theory_flag_promotion_fails(self):
        value = self.value()
        value["claim_flags"]["lorentzian_full_theory_certified"] = True
        self.assertTrue(verify(result=value)[0])

    def test_report_drift_fails(self):
        self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__":
    unittest.main()
