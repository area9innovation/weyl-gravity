"""Tests for the complete transverse rank-310 SDR first variation."""

import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_rank310_dual_sdr import (
    abstract_fixture,
    coefficient_fixture,
)


class NariaiTransverseCompleteRank310SDRFirstVariationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.abstract = abstract_fixture()
        cls.coefficient = coefficient_fixture()

    def test_all_twenty_one_matrix_identities(self):
        self.assertEqual(len(self.abstract["defects"]), 21)
        self.assertFalse(any(self.abstract["defects"].values()))

    def test_all_ten_blocks_are_retained(self):
        dotted = self.abstract["dotted"]
        self.assertEqual(len(dotted["q_dot"]), 10)
        self.assertEqual(len(dotted["original_q_dot"]), 10)
        self.assertEqual(len(dotted["inclusion_dot"]), 10)
        self.assertEqual(len(dotted["projection_dot"][0]), 10)

    def test_coefficient_relations(self):
        self.assertFalse(any(self.coefficient["coefficient_defect_counts"].values()))

    def test_new_complement_variations_are_serialized(self):
        self.assertGreater(self.coefficient["d_aut_dot"]["nonzero_coefficients"], 0)
        self.assertGreater(self.coefficient["g_dot"]["nonzero_coefficients"], 0)

    def test_action_Bach_only_requests_point_coefficient_jet(self):
        self.assertEqual(self.coefficient["requested_coefficient_jets"]["B_action"], [[]])


if __name__ == "__main__":
    unittest.main()
