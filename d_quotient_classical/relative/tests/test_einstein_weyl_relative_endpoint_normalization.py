from __future__ import annotations

import unittest

from d_quotient_classical.relative.einstein_weyl_relative_endpoint_normalization import build, validate


class RelativeEndpointNormalizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.value = build()

    def test_schema_and_formula(self):
        validate(self.value)
        self.assertEqual(self.value["derivation"]["forced_formula"], "A2(P_X^4)=X^mu c_mu_star")
        self.assertEqual([item["generator"] for item in self.value["A2"]], ["H", "P_x", "J_1", "J_2", "J_3"])

    def test_pairing_sign_and_excluded_rows(self):
        self.assertEqual(self.value["derivation"]["orientation_sign"], 1)
        targets = {term["row"] for item in self.value["A2"] for term in item["target_terms"]}
        self.assertFalse({"lambda_cov_star", "sigma_W_star"} & targets)

    def test_pointwise_vs_global_rank(self):
        base = self.value["equatorial_basepoint_values"]
        self.assertEqual(base["pointwise_rank"], 4)
        self.assertEqual(base["global_map_rank"], 5)
        self.assertIn("nonzero global Killing field", base["rank_note"])

    def test_fail_closed(self):
        flags = self.value["classification"]
        self.assertTrue(flags["endpoint_normalization_exact"])
        self.assertFalse(flags["endpoint_normalized_order_zero_chain_map_exists"])
        self.assertFalse(flags["positive_order_chain_map_ruled_out"])
        self.assertFalse(flags["support_local_chain_map_A_constructed"])
        self.assertFalse(flags["relative_q2_repaired"])


if __name__ == "__main__":
    unittest.main()
