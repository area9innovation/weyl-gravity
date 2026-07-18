"""Tests for the factorized transverse endpoint completion."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_factorized_endpoint_completion import exact_data


class NariaiTransverseFactorizedEndpointCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_base_reconciles_with_action(self):
        base = self.data["base_reconciliation"]
        self.assertEqual(base["correction"]["nonzero_coefficients"], 15)
        self.assertGreater(base["historical_Q_base_defect"]["nonzero_coefficients"], 0)
        self.assertEqual(base["endpoint_plus_2_B_action_defect"]["nonzero_coefficients"], 0)
        self.assertFalse(base["historical_post_normal_order_Q_authoritative"])

    def test_complete_ansatz_has_unique_algebraic_solution(self):
        solve = self.data["complete_first_order_solve"]
        self.assertEqual(solve["total_unknowns"], 405)
        self.assertEqual(solve["coefficient_map_shape"], [60, 45])
        self.assertEqual(solve["coefficient_map_rank"], 45)
        self.assertEqual(solve["augmented_ranks"], [45] * 9)
        self.assertEqual(solve["free_parameter_counts"], [0] * 9)
        self.assertEqual(solve["unique_correction"]["nonzero_coefficients"], 15)
        self.assertEqual(solve["unique_correction"]["orders"], [0])

    def test_endpoint_target_is_gauge_closed_and_cyclic(self):
        target = self.data["factorized_endpoint_target"]
        self.assertTrue(target["Qdot_is_order_zero"])
        self.assertTrue(target["endpoint_factorized_cyclic"])
        self.assertTrue(target["endpoint_gauge_closed"])
        self.assertEqual(target["Qdot_fibre_adjoint_defect"]["nonzero_coefficients"], 0)
        self.assertNotEqual(
            target["compressed_parent_endpoint_variation"]["sha256"],
            target["action_bach_variation_target"]["sha256"],
        )
        self.assertEqual(
            target["compressed_parent_endpoint_variation"]["nonzero_coefficients"],
            target["action_bach_variation_target"]["nonzero_coefficients"],
        )

    def test_action_comparison_remains_open(self):
        disposition = self.data["disposition"]
        self.assertTrue(disposition["unique_factorized_endpoint_completion"])
        self.assertFalse(disposition["action_third_variation_independently_derived"])
        self.assertFalse(disposition["rank_310_first_variation_SDR"])
        self.assertFalse(disposition["transverse_causal_transfer"])


if __name__ == "__main__":
    unittest.main()
