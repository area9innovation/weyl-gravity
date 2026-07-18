"""Tests for the transverse upper relative-saddle chain."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_relative_saddle_upper_chain import exact_data


class NariaiTransverseRelativeSaddleUpperChainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_upper_chain_closes(self):
        identity = self.data["typed_identity"]
        self.assertEqual(identity["domain"], "C0")
        self.assertEqual(identity["codomain"], "H1dual")
        self.assertEqual(identity["base_defect"]["nonzero_coefficients"], 0)
        self.assertEqual(identity["first_variation_defect"]["nonzero_coefficients"], 0)

    def test_jet_coverage_is_inside_certified_envelope(self):
        coverage = self.data["coefficient_jet_coverage"]
        self.assertEqual(coverage["certified_curvature_maximum_order"], 5)
        self.assertLessEqual(coverage["incidence_p0"]["maximum_order"], 4)
        self.assertLessEqual(coverage["parent_middle"]["maximum_order"], 2)
        self.assertTrue(coverage["above_maximum_fails_closed"])

    def test_remaining_gate_is_fail_closed(self):
        disposition = self.data["disposition"]
        self.assertTrue(disposition["upper_relative_saddle_chain_exact"])
        self.assertFalse(disposition["transverse_action_Bach_Hessian_variation_available"])
        self.assertFalse(disposition["complete_rank_310_first_variation_SDR"])
        self.assertFalse(disposition["transverse_causal_transfer"])


if __name__ == "__main__":
    unittest.main()
