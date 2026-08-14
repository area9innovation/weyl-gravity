from __future__ import annotations

import copy
import unittest

from foundations.build_ngc3198_common_fit_comparison import build, canonical_digest
from foundations.check_ngc3198_common_fit_comparison import check
from foundations.verify_ngc3198_common_fit_comparison import verify


class Ngc3198CommonFitComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.value = build()

    def test_same_protocol_has_three_controls(self):
        by_id = {item["model_id"]: item for item in self.value["models"]}
        self.assertEqual(set(by_id), {"NEWTONIAN_BARYONS_ONLY", "GR_NFW_DARK_HALO", "MANNHEIM_CONFORMAL_GRAVITY"})
        self.assertTrue(by_id["GR_NFW_DARK_HALO"]["random_error_gate"]["passed"])
        self.assertFalse(by_id["MANNHEIM_CONFORMAL_GRAVITY"]["random_error_gate"]["passed"])
        self.assertFalse(by_id["NEWTONIAN_BARYONS_ONLY"]["random_error_gate"]["passed"])

    def test_weighted_and_unweighted_metrics_are_not_conflated(self):
        by_id = {item["model_id"]: item for item in self.value["models"]}
        self.assertLess(by_id["MANNHEIM_CONFORMAL_GRAVITY"]["metrics"]["unweighted_rms_residual_km_s"], by_id["GR_NFW_DARK_HALO"]["metrics"]["unweighted_rms_residual_km_s"])
        self.assertGreater(by_id["MANNHEIM_CONFORMAL_GRAVITY"]["metrics"]["chi_squared"], by_id["GR_NFW_DARK_HALO"]["metrics"]["chi_squared"])

    def test_no_theory_selection_promotion(self):
        tampered = copy.deepcopy(self.value)
        tampered["claim_flags"]["complete_theory_selected"] = True
        tampered["canonical_digest"] = canonical_digest(tampered)
        self.assertIn("complete-theory boundary", check(tampered)[0])

    def test_independent_verifier(self): self.assertEqual(verify()[0], [])


if __name__ == "__main__": unittest.main()
