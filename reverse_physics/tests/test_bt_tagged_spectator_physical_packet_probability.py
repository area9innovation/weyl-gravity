import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_tagged_spectator_physical_packet_probability import CERT, verify


class TaggedSpectatorPhysicalPacketProbabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_second_spectator(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_tagged_spectator_witness"]["zero_subsets"]["2"].append([1, 4])
        self.assert_rejected(mutation)

    def test_rejects_three_leg_component(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_tagged_spectator_witness"]["zero_subsets"]["3"] = [[0, 1, 3]]
        self.assert_rejected(mutation)

    def test_rejects_partition_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["partition_and_order_classification"]["supported_disconnected_partitions"] = []
        self.assert_rejected(mutation)

    def test_rejects_lower_connected_six_point_order(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["partition_and_order_classification"]["order_four"] = "connected six-point tree already occurs at lambda2"
        self.assert_rejected(mutation)

    def test_rejects_wrong_jet_norm(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["four_point_positive_jet_factorization"]["jet_norm"] = "r4^sharp*r4=12"
        self.assert_rejected(mutation)

    def test_rejects_wrong_born_coefficient(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["four_point_positive_jet_factorization"]["Born_rate"] = "d_sigma/d_Omega=lambda^4/(32*pi^2*s)"
        self.assert_rejected(mutation)

    def test_rejects_wrong_probability_order(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["complete_leading_tagged_probability"]["general_coefficient"] = "q_click=O(lambda^8)"
        self.assert_rejected(mutation)

    def test_rejects_missing_beam_area(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["complete_leading_tagged_probability"]["beam_normalization"] = "cross section is already a probability"
        self.assert_rejected(mutation)

    def test_rejects_forward_dependency(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["complete_leading_tagged_probability"]["forward_independence"] = "forward graph is required"
        self.assert_rejected(mutation)

    def test_rejects_cross_stratum_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["hard_nonforward_stratified_atlas"]["cross_stratum_detector"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_all_order_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("an exact probability after summing all perturbative orders")
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("anything LORENTZIAN-CAUSAL")
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
