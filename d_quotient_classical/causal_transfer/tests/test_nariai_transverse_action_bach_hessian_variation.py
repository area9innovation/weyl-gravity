"""Tests for the transverse action Bach-Hessian variation."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_action_bach_hessian_variation import (
    exact_data,
)


class NariaiTransverseActionBachHessianVariationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_direct_action_order_two_matches(self):
        direct = self.data["direct_action_leading_derivation"]
        compare = self.data["parent_action_comparison"]
        self.assertTrue(direct["orders_above_two_absent"])
        self.assertEqual(direct["base_action_defect"]["nonzero_coefficients"], 0)
        self.assertEqual(compare["direct_order_two_defect"]["nonzero_coefficients"], 0)

    def test_parent_action_normalization_is_explicit(self):
        compare = self.data["parent_action_comparison"]
        self.assertEqual(compare["normalization_defect"]["nonzero_coefficients"], 0)
        self.assertNotEqual(
            compare["compressed_parent_endpoint_variation"]["sha256"],
            compare["action_bach_variation_target"]["sha256"],
        )

    def test_lower_completion_is_unique(self):
        lower = self.data["lower_order_noether_completion"]
        self.assertEqual(lower["total_unknowns"], 405)
        self.assertEqual(lower["coefficient_map_shape"], [60, 45])
        self.assertEqual(lower["coefficient_map_rank"], 45)
        self.assertEqual(lower["augmented_ranks"], [45] * 9)
        self.assertEqual(lower["free_parameter_counts"], [0] * 9)
        self.assertTrue(lower["unique_completion"])

    def test_frozen_lower_terms_are_not_evidence(self):
        direct = self.data["direct_action_leading_derivation"]
        self.assertFalse(direct["frozen_lower_table_authoritative"])
        self.assertGreater(direct["frozen_lower_target_defect"]["nonzero_coefficients"], 0)

    def test_downstream_gates_remain_false(self):
        disposition = self.data["disposition"]
        self.assertTrue(disposition["action_bach_hessian_variation_exact"])
        self.assertFalse(disposition["rank_310_first_variation_SDR"])
        self.assertFalse(disposition["transverse_causal_transfer"])


if __name__ == "__main__":
    unittest.main()
