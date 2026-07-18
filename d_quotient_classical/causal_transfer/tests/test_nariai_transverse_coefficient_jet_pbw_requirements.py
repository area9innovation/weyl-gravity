"""Tests for the transverse coefficient-jet PBW requirements gate."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_coefficient_jet_pbw_requirements import (
    exact_data,
)


class NariaiTransverseCoefficientJetRequirementsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_independent_fixture_matches(self):
        theorem = self.data["backend_theorem"]
        self.assertTrue(theorem["direct_polynomial_fixture_associator_zero"])
        self.assertTrue(theorem["backend_associator_zero"])
        self.assertTrue(theorem["direct_and_backend_coefficient_jets_agree"])
        self.assertEqual(len(theorem["checked_output_coefficient_jet_orders"]), 4)

    def test_nariai_missing_input_is_exactly_scoped(self):
        requirements = self.data["nariai_replay_requirements"]
        self.assertTrue(requirements["curvature_jet_input_sufficient"])
        self.assertEqual(
            len(requirements["corrected_L0_positive_coefficient_jet_words_required_for_first_square"]),
            4,
        )
        self.assertEqual(
            len(requirements["corrected_L1_positive_coefficient_jet_words_required_for_associativity"]),
            14,
        )
        self.assertFalse(requirements["positive_order_corrected_splitting_jets_available"])
        self.assertFalse(requirements["point_values_determine_positive_jets"])

    def test_no_transverse_sdr_overclaim(self):
        disposition = self.data["disposition"]
        self.assertTrue(disposition["associative_coefficient_jet_backend_available"])
        self.assertFalse(disposition["nariai_associative_replay_runnable"])
        self.assertFalse(disposition["rank_310_transverse_SDR_decided"])


if __name__ == "__main__":
    unittest.main()
