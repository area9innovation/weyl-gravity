import json
import unittest
from foundations.verify_normal_hyperbolic_factor_atlas import LEDGER, REPORT, RESULT, verify


class NormalHyperbolicFactorAtlasTests(unittest.TestCase):
    def test_repository_result(self): self.assertEqual([], verify()[0])
    def test_action_promotion_fails(self):
        value = json.loads(RESULT.read_text()); value["cell_actions"][0]["old"] = "LOCAL_RESULT"
        self.assertTrue(verify(result=value)[0])
    def test_source_pin_fails(self):
        ledger = json.loads(LEDGER.read_text()); ledger["entries"][0]["artifact"]["sha256"] = "0" * 64
        self.assertTrue(verify(ledger=ledger)[0])
    def test_reverse_claim_fails(self):
        value = json.loads(RESULT.read_text()); value["claim_flags"]["reverse_math_strength_proved"] = True
        self.assertTrue(verify(result=value)[0])
    def test_report_drift_fails(self): self.assertTrue(verify(report=REPORT.read_text() + "drift\n")[0])


if __name__ == "__main__": unittest.main()
