"""Tests for transverse corrected-BGG splitting coefficient jets."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_corrected_bgg_splitting_coefficient_jets import (
    exact_data,
)


class NariaiTransverseCorrectedSplittingJetsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_derivation_is_not_interpolation(self):
        self.assertFalse(self.data["derivation"]["interpolation_used"])
        self.assertIn("covariant HPL", self.data["derivation"]["L0"])
        self.assertIn("unique algebraic left factor", self.data["derivation"]["L1_correction"])

    def test_strict_square_closes_on_every_required_jet(self):
        square = self.data["strict_square"]
        self.assertEqual(square["base_defect_coefficients"], 0)
        self.assertTrue(square["all_required_jets_zero"])
        self.assertEqual(len(square["coefficient_jet_defects"]), 15)
        self.assertEqual(set(square["coefficient_jet_defects"].values()), {0})

    def test_point_values_are_recovered(self):
        comparison = self.data["superseded_point_replay_comparison"]
        self.assertEqual(comparison["L0_point_defect"]["nonzero_coefficients"], 0)
        self.assertEqual(comparison["L1_point_defect"]["nonzero_coefficients"], 0)
        self.assertTrue(comparison["old_point_values_authoritative_after_associative_replay"])

    def test_next_gate_stays_open(self):
        disposition = self.data["disposition"]
        self.assertTrue(disposition["corrected_splitting_coefficient_jets_complete"])
        self.assertTrue(disposition["associative_M_L1_K_replay_ready"])
        self.assertFalse(disposition["middle_and_schur_replayed"])
        self.assertFalse(disposition["rank_310_transverse_SDR_decided"])


if __name__ == "__main__":
    unittest.main()
