import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_finite_time_active_loop_affiliation import CERT, verify


class FiniteTimeActiveLoopAffiliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def mutate(self, path, value):
        mutation = copy.deepcopy(self.certificate)
        target = mutation
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        self.assert_rejected(mutation)

    def test_rejects_lifecycle_mutation(self):
        self.mutate(("lifecycle_state",), "CLASSIFIED")

    def test_rejects_ordered_kernel_mutation(self):
        self.mutate(("ordered_dyson_kernel", "dispersive_interference"), "wrong")

    def test_rejects_resonant_cut_mixing(self):
        self.mutate(("ordered_dyson_kernel", "resonant_value"), "Kdisp_T(0)=T")

    def test_rejects_fejer_normalization_mutation(self):
        self.mutate(("fejer_affiliation", "normalization"), "int K=2")

    def test_rejects_bubble_sign_mutation(self):
        self.mutate(("finite_time_bubble", "general_formula"), "B_T=B+C+C")

    def test_rejects_tagged_gap_mutation(self):
        self.mutate(("tagged_fixture", "bubble_sum"), "wrong")

    def test_rejects_tagged_frame_suppression(self):
        self.mutate(("tagged_fixture", "frame"), "Lorentz invariant")

    def test_rejects_loop_normalization_mutation(self):
        self.mutate(("tagged_fixture", "local_loop_click"), "wrong")

    def test_rejects_window_frame_mutation(self):
        self.mutate(("hard_window", "definition"), "unspecified frame")

    def test_rejects_packet_bound_mutation(self):
        self.mutate(("compact_packet", "bound"), "unbounded")

    def test_rejects_q6_promotion(self):
        self.mutate(("interpretation", "complete_tagged_q6_probability"), "COMPUTED")

    def test_rejects_eq19_promotion(self):
        self.mutate(("interpretation", "general_Eq19"), "PROVED")

    def test_rejects_gravity_promotion(self):
        self.mutate(("interpretation", "gravity_or_BV_BRST_transfer"), "CONSTRUCTED")

    def test_rejects_lorentzian_promotion(self):
        self.mutate(("interpretation", "Lorentzian_causal_claim"), "ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
