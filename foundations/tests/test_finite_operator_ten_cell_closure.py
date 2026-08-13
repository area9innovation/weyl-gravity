import copy
import unittest

from foundations.verify_finite_operator_ten_cell_closure import RESULT, REPORT, load, verify


class FiniteOperatorTenCellClosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load(RESULT)
        cls.report = REPORT.read_text()

    def test_certificate(self):
        self.assertEqual([], verify())

    def test_exact_status_split(self):
        statuses = [item["new_status"] for item in self.result["promotions"]]
        self.assertEqual(9, statuses.count("LOCAL_RESULT"))
        self.assertEqual(1, statuses.count("PIECES_ONLY"))

    def test_continuum_promotion_fails_closed(self):
        result = copy.deepcopy(self.result)
        renorm = next(item for item in result["promotions"] if item["coordinate"]["obligation"] == "RENORMALIZED_PRODUCTS")
        renorm["new_status"] = "LOCAL_RESULT"
        self.assertTrue(verify(result=result))

    def test_boundary_flag_fails_closed(self):
        result = copy.deepcopy(self.result)
        result["claim_flags"]["continuum_renormalized_products_constructed"] = True
        self.assertTrue(verify(result=result))

    def test_report_boundary_fails_closed(self):
        self.assertTrue(verify(report=self.report.replace("cutoff products do not become continuum renormalized", "cutoff products establish continuum renormalized")))


if __name__ == "__main__":
    unittest.main()
