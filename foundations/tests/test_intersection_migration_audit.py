import copy
import unittest

from foundations.verify_intersection_migration_audit import REPORT, RESULT, load, verify


class IntersectionMigrationAuditTests(unittest.TestCase):
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

    def test_blind_transfer_fails(self):
        result = copy.deepcopy(self.result)
        decision = next(x for x in result["decisions"] if x["decision"] == "REVIEWED_NO_TRANSFER")
        decision["resulting_coverage_status"] = "PRIORITY_GAP"
        self.assertTrue(verify(result=result)[0])

    def test_absence_promotion_fails(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["reviewed_no_transfer_means_literature_absent"] = True
        self.assertTrue(verify(result=result)[0])

    def test_report_boundary_fails(self):
        report = self.report.replace("not a literature-absence claim", "a literature-absence claim")
        self.assertTrue(verify(report=report)[0])


if __name__ == "__main__":
    unittest.main()
