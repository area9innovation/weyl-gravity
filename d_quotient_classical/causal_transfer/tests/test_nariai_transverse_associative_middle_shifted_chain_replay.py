"""Tests for the associative transverse parent-middle replay."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_associative_middle_shifted_chain_replay import (
    exact_data,
)


class NariaiTransverseAssociativeMiddleReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_typed_associator_zero(self):
        replay = self.data["typed_replay"]
        self.assertEqual(replay["base_associator_coefficients"], 0)
        self.assertEqual(replay["variation_associator_coefficients"], 0)
        self.assertEqual(replay["middle_coefficient_jet_words_requested"], [[]])

    def test_parent_and_shifted_chain_zero(self):
        self.assertEqual(self.data["parent_identity"]["variation_defect_coefficients"], 0)
        shifted = self.data["shifted_chain"]
        self.assertEqual(shifted["base_defect_coefficients"], 0)
        self.assertEqual(shifted["variation_defect_coefficients"], 0)
        self.assertEqual(shifted["old_backend_reported_coefficients"], 207)
        self.assertFalse(shifted["old_backend_defect_authoritative"])

    def test_phi_and_boundary(self):
        self.assertEqual(self.data["authoritative_phi_variation"]["nonzero_coefficients"], 415)
        disposition = self.data["disposition"]
        self.assertTrue(disposition["associative_parent_middle_replay_complete"])
        self.assertFalse(disposition["compressed_schur_replayed"])
        self.assertFalse(disposition["rank_310_transverse_SDR_decided"])


if __name__ == "__main__":
    unittest.main()
