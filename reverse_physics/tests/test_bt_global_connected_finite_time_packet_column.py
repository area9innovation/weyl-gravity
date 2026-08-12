import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_global_connected_finite_time_packet_column import CERT, verify


class GlobalConnectedFiniteTimePacketColumnTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_soft_rank_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["soft_zero_geometry"]["effective_transverse_rank"] = 3
        self.assert_rejected(mutation)

    def test_rejects_soft_determinant_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["soft_zero_geometry"]["Jacobian_determinant"] = "0"
        self.assert_rejected(mutation)

    def test_rejects_exchange_integral_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_exchange_integral"]["exchange_channel_value"] = "DIVERGENT"
        self.assert_rejected(mutation)

    def test_rejects_angular_primitive_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_exchange_integral"]["angular_reduction"] = "0"
        self.assert_rejected(mutation)

    def test_rejects_hard_integral_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_exchange_integral"]["hard_channel_value"] = "0"
        self.assert_rejected(mutation)

    def test_rejects_kernel_bound_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["global_connected_column"]["kernel_sum_bound"] = "INFINITE"
        self.assert_rejected(mutation)

    def test_rejects_amplitude_bound_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["global_connected_column"]["operator_bound"] = "UNBOUNDED"
        self.assert_rejected(mutation)

    def test_rejects_scalar_bound_change(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["declared_scalar_source"]["global_bound"] = "UNKNOWN"
        self.assert_rejected(mutation)

    def test_rejects_all_time_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["all_time_limit"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_disconnected_object_removal(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["missing_object_ledger"].pop(0)
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("anything LORENTZIAN-CAUSAL")
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
