import copy
import unittest

from foundations.verify_finite_brst_twenty_cell_closure import RESULT, REPORT, load, verify


class FiniteBrstTwentyCellClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.report = REPORT.read_text()

    def test_certificate(self):
        self.assertEqual([], verify())

    def test_exact_status_split(self):
        statuses = [item["new_status"] for item in self.result["promotions"]]
        self.assertEqual((17, 3), (statuses.count("LOCAL_RESULT"), statuses.count("PIECES_ONLY")))

    def test_product_promotion_fails_closed(self):
        result = copy.deepcopy(self.result)
        item = next(item for item in result["promotions"] if item["coordinate"]["obligation"] == "RENORMALIZED_PRODUCTS")
        item["new_status"] = "LOCAL_RESULT"
        self.assertTrue(verify(result=result))

    def test_weyl_qme_promotion_fails_closed(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["weyl_qme_restored"] = True
        self.assertTrue(verify(result=result))

    def test_report_order_fails_closed(self):
        self.assertTrue(verify(report=self.report.replace("classified before any QME", "classified after the QME")))


if __name__ == "__main__":
    unittest.main()
