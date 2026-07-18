"""Tests for the factorized transverse Hom-adjoint and Schur replay."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_factorized_hom_schur_replay import (
    exact_data,
)


class NariaiTransverseFactorizedHomSchurReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_order_five_jet_layer_is_exercised(self):
        jets = self.data["jet_coverage"]
        self.assertEqual(jets["certified_curvature_max_order"], 5)
        self.assertEqual(jets["L1_max_requested_order"], 4)
        self.assertEqual(jets["curvature_max_requested_order"], 5)
        self.assertGreater(jets["L1_requested_word_count"], 14)

    def test_factorized_adjoint_rejects_normal_table_shortcut(self):
        adjoint = self.data["factorized_Hom_adjoint"]
        self.assertFalse(adjoint["naive_normal_table_adjoint_authoritative"])
        self.assertGreater(adjoint["naive_normal_table_base_defect"]["nonzero_coefficients"], 0)
        self.assertGreater(adjoint["naive_normal_table_variation_defect"]["nonzero_coefficients"], 0)

    def test_middle_and_schur_close(self):
        middle = self.data["parent_middle"]
        self.assertEqual(middle["base_defect"]["nonzero_coefficients"], 0)
        self.assertEqual(middle["old_point_defect"]["nonzero_coefficients"], 0)
        self.assertTrue(middle["factorized_formal_self_adjoint"])
        schur = self.data["compressed_schur"]
        self.assertEqual(schur["phi_base_defect"]["nonzero_coefficients"], 0)
        self.assertEqual(schur["phi_variation_defect"]["nonzero_coefficients"], 0)
        self.assertTrue(schur["factorized_cyclic"])

    def test_upper_chain_remains_fail_closed(self):
        upper = self.data["next_gate_requirements"]
        self.assertEqual(upper["current_certified_curvature_coefficient_jet_order"], 5)
        self.assertFalse(upper["upper_chain_replayed"])
        disposition = self.data["disposition"]
        self.assertFalse(disposition["rank_310_transverse_SDR_decided"])
        self.assertFalse(disposition["transverse_causal_transfer"])


if __name__ == "__main__":
    unittest.main()
