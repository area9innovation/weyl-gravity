import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_tagged_connected_finite_time_interference import CERT, verify


class TaggedConnectedFiniteTimeInterferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_channel_momentum_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["tagged_fixture_and_channels"]["channels"][2]["q"][0] = "7/5"
        self.assert_rejected(mutation)

    def test_rejects_channel_delta_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["tagged_fixture_and_channels"]["channels"][2]["delta"] = "1/5"
        self.assert_rejected(mutation)

    def test_rejects_resonance_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["tagged_fixture_and_channels"]["channels"][1]["resonant"] = False
        self.assert_rejected(mutation)

    def test_rejects_resonant_mask_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["tagged_fixture_and_channels"]["resonant_masks"][0] = 7
        self.assert_rejected(mutation)

    def test_rejects_tag_odd_partition_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["tagged_fixture_and_channels"]["R_tag_odd_masks"][0] = 11
        self.assert_rejected(mutation)

    def test_rejects_tagged_embedding_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["common_positive_external_jet_carrier"]["tagged_embedding_vector"][0] = 1
        self.assert_rejected(mutation)

    def test_rejects_tagged_norm_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["common_positive_external_jet_carrier"]["tagged_norm"] = "d^T*d=23"
        self.assert_rejected(mutation)

    def test_rejects_incidence_weight_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["common_positive_external_jet_carrier"]["incidence_pairing"] = "<d,a_T>=sqrt(2)/2*(4*sum_(A in R)beta_A,T+6*sum_(A in N)beta_A,T)"
        self.assert_rejected(mutation)

    def test_rejects_real_bracket_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_tree_interference_kernel"]["real_bracket"] = mutation["exact_tree_interference_kernel"]["real_bracket"].replace("125*sin(16*T/5)/256", "124*sin(16*T/5)/256")
        self.assert_rejected(mutation)

    def test_rejects_linear_resonance_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_tree_interference_kernel"]["resonant_contribution"] = "6*sum_(A in N)Re(beta_A,T)=11*T"
        self.assert_rejected(mutation)

    def test_rejects_lower_bound_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_tree_interference_kernel"]["strict_lower_bound"] = "W(T)>=0"
        self.assert_rejected(mutation)

    def test_rejects_small_time_slope_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_tree_interference_kernel"]["small_time_slope"] = "W'(0)=0"
        self.assert_rejected(mutation)

    def test_rejects_large_time_coefficient_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_tree_interference_kernel"]["large_time_limit"] = "lim_(T->infinity) W(T)/T=11"
        self.assert_rejected(mutation)

    def test_rejects_restored_multiplier_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["exact_tree_interference_kernel"]["restored_cross_kernel"] = "I_tree^(6)=8*sqrt(2)*lambda^6*W(T)"
        self.assert_rejected(mutation)

    def test_rejects_false_decoupling(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["tree_sector_decoupling"] = "TRUE"
        self.assert_rejected(mutation)

    def test_rejects_normalized_probability_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["normalized_cross_stratum_packet_probability"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_complete_lambda6_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["complete_order_lambda6_probability"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_loop_completion_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["loop_and_survival_completion"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["general_Eq19"] = "PROVED"
        self.assert_rejected(mutation)

    def test_rejects_gravity_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["gravity_or_BV_BRST_transfer"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["Lorentzian_causal_claim"] = "ESTABLISHED"
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
