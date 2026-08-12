"""Falsification tests for the continuous hard-angle BT q6 family."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_continuous_angle_q6_family import CERT, verify


class ContinuousAngleQ6FamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def mutated(self):
        return copy.deepcopy(self.certificate)

    def reject(self, value):
        self.assertFalse(all(verify(value).values()))

    def test_independent_verifier(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_domain_endpoint_promotion(self):
        value = self.mutated()
        value["continuous_tagged_family"]["domain"] = "-1<=c<=1"
        self.reject(value)

    def test_rejects_s_invariant_mutation(self):
        value = self.mutated()
        value["continuous_tagged_family"]["active_invariants"]["s"] = "63*kappa^2/25"
        self.reject(value)

    def test_rejects_t_invariant_mutation(self):
        value = self.mutated()
        value["continuous_tagged_family"]["active_invariants"]["t"] = "-32*(1+c)*kappa^2/25"
        self.reject(value)

    def test_rejects_channel_momentum_mutation(self):
        value = self.mutated()
        value["ten_channel_kinematics"]["rows"][2]["q"][2] = "0"
        self.reject(value)

    def test_rejects_channel_invariant_mutation(self):
        value = self.mutated()
        value["ten_channel_kinematics"]["rows"][4]["q_squared"] = "0"
        self.reject(value)

    def test_rejects_channel_delta_mutation(self):
        value = self.mutated()
        value["ten_channel_kinematics"]["rows"][8]["delta"] = "0"
        self.reject(value)

    def test_rejects_channel_denominator_mutation(self):
        value = self.mutated()
        value["ten_channel_kinematics"]["rows"][9]["D"] = "2"
        self.reject(value)

    def test_rejects_channel_weight_mutation(self):
        value = self.mutated()
        value["ten_channel_kinematics"]["rows"][0]["weight"] = 6
        self.reject(value)

    def test_rejects_resonant_family_mutation(self):
        value = self.mutated()
        value["ten_channel_kinematics"]["rows"][1]["family"] = "T_EXCHANGE"
        self.reject(value)

    def test_rejects_exchange_formula_mutation(self):
        value = self.mutated()
        value["ten_channel_kinematics"]["exchange_formulas"]["a_t"] = "0"
        self.reject(value)

    def test_rejects_tree_lower_step_mutation(self):
        value = self.mutated()
        value["continuous_tree_cross"]["lower_bound_steps"][2] = "10*sin(a_t*T)/(-t)>=0"
        self.reject(value)

    def test_rejects_tree_lower_bound_mutation(self):
        value = self.mutated()
        value["continuous_tree_cross"]["uniform_lower_bound"] = "W(c,T)>=0"
        self.reject(value)

    def test_rejects_small_time_slope_mutation(self):
        value = self.mutated()
        value["continuous_tree_cross"]["small_time_slope"] = "W_T(c,0)=0"
        self.reject(value)

    def test_rejects_large_time_coefficient_mutation(self):
        value = self.mutated()
        value["continuous_tree_cross"]["large_time_limit"] = "lim W/T=0"
        self.reject(value)

    def test_rejects_loop_t_gap_mutation(self):
        value = self.mutated()
        value["continuous_finite_time_loop"]["light_cone_gaps"]["t"][0] = "0"
        self.reject(value)

    def test_rejects_loop_formula_mutation(self):
        value = self.mutated()
        value["continuous_finite_time_loop"]["bubble_sum"] = "B_*=0"
        self.reject(value)

    def test_rejects_fixture_regression_mutation(self):
        value = self.mutated()
        value["continuous_finite_time_loop"]["fixture_regression"] = "B_*(0)=0"
        self.reject(value)

    def test_rejects_packet_d0_promotion(self):
        value = self.mutated()
        value["compact_angle_bounds"]["tree_pointwise_bound"] = "|W|<=27*T on every packet tube"
        self.reject(value)

    def test_rejects_transient_bound_mutation(self):
        value = self.mutated()
        value["compact_angle_bounds"]["transient_bound"] = "|B_*-L-6|<=0"
        self.reject(value)

    def test_rejects_relative_bound_without_d0(self):
        value = self.mutated()
        value["compact_angle_bounds"]["relative_bound"] = "|R6|<=1"
        self.reject(value)

    def test_rejects_relative_probability_mutation(self):
        value = self.mutated()
        value["complete_probability_family"]["relative_coefficient"] = "R6=0"
        self.reject(value)

    def test_rejects_probability_order_mutation(self):
        value = self.mutated()
        value["complete_probability_family"]["probability"] = "q=q4+O(lambda^6)"
        self.reject(value)

    def test_rejects_angle_coherence_promotion(self):
        value = self.mutated()
        value["disposition"]["coherent_superposition_of_angle_records"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_endpoint_promotion(self):
        value = self.mutated()
        value["disposition"]["forward_and_backward_endpoints"] = "INCLUDED"
        self.reject(value)

    def test_rejects_Eq19_promotion(self):
        value = self.mutated()
        value["disposition"]["general_Eq19"] = "PROVED"
        self.reject(value)

    def test_rejects_gravity_promotion(self):
        value = self.mutated()
        value["disposition"]["gravity_or_metric_BV_BRST_transfer"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_Lorentzian_boundary_removal(self):
        value = self.mutated()
        value["does_not_establish"] = [
            row for row in value["does_not_establish"] if "LORENTZIAN-CAUSAL" not in row
        ]
        self.reject(value)

    def test_rejects_input_hash_mutation(self):
        value = self.mutated()
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.reject(value)


if __name__ == "__main__":
    unittest.main()
