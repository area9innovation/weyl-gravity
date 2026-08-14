import copy
import unittest

from foundations.verify_full_surface_gap_audit import RESULT, REPORT, load, verify


class FullSurfaceGapAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.report = REPORT.read_text()

    def test_certificate(self):
        self.assertEqual([], verify())

    def test_exact_partition(self):
        counts = {state: sum(item["prior_surface_state"] == state for item in self.result["decisions"]) for state in ("EMITTED_NOT_MAPPED", "SYNTHETIC_NOT_EMITTED")}
        self.assertEqual({"EMITTED_NOT_MAPPED": 51, "SYNTHETIC_NOT_EMITTED": 124}, counts)

    def test_positive_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["decisions"][0]["new_status"] = "LOCAL_RESULT"
        self.assertTrue(verify(result=result))

    def test_absence_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["literature_absence_proved"] = True
        self.assertTrue(verify(result=result))

    def test_report_boundary_fails(self):
        self.assertTrue(verify(report=self.report.replace("do not license evidence transfer", "license evidence transfer")))


if __name__ == "__main__":
    unittest.main()
