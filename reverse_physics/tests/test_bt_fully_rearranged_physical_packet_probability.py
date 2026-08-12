import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_fully_rearranged_physical_packet_probability import CERT, verify


class FullyRearrangedPhysicalPacketProbabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_soft_center(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_detector_witness"]["minimum_external_energy"] = "0"
        self.assert_rejected(mutation)

    def test_rejects_collinear_center(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_detector_witness"]["minimum_same_side_pair_invariant"] = "0"
        self.assert_rejected(mutation)

    def test_rejects_spectator_diagonal(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_detector_witness"]["minimum_cross_Euclidean_distance_squared"] = "0"
        self.assert_rejected(mutation)

    def test_rejects_three_component_delta(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_detector_witness"]["minimum_component_momentum_sum_Euclidean_squares"]["3"] = "0"
        self.assert_rejected(mutation)

    def test_rejects_partition_count_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_support_classification"]["disconnected_set_partitions"] = 201
        self.assert_rejected(mutation)

    def test_rejects_profile_removal(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_support_classification"]["size_profiles"].pop()
        self.assert_rejected(mutation)

    def test_rejects_nonzero_disconnected_pairing(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["disconnected_support_classification"]["detector_pairing"] = "UNKNOWN"
        self.assert_rejected(mutation)

    def test_rejects_lower_amplitude_order(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["complete_leading_physical_probability"]["first_connected_six_leg_order"] = "lambda^2"
        self.assert_rejected(mutation)

    def test_rejects_wrong_probability_order(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["complete_leading_physical_probability"]["leading_click"] = "q_click=lambda^4"
        self.assert_rejected(mutation)

    def test_rejects_forward_dependency(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["leading_forward_graph_needed_for_click"] = "YES"
        self.assert_rejected(mutation)

    def test_rejects_all_order_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["all_order_probability"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("anything LORENTZIAN-CAUSAL")
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
