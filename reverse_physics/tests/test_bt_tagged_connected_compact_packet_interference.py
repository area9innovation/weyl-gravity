import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_tagged_connected_compact_packet_interference import CERT, verify


class TaggedConnectedCompactPacketInterferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_measure_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_packet_carrier"]["one_particle_measure"] = "d^3p/E_p"
        self.assert_rejected(mutation)

    def test_rejects_identity_overlap_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_packet_carrier"]["identity_overlap"] = "c_fg=1"
        self.assert_rejected(mutation)

    def test_rejects_mask_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_tree_cross_functional"]["mask_sets"]["N"][0] = 7
        self.assert_rejected(mutation)

    def test_rejects_incidence_bound_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_tree_cross_functional"]["pointwise_bound"] = "|W|<=48*T/d0"
        self.assert_rejected(mutation)

    def test_rejects_relative_cross_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_tree_cross_functional"]["relative_tree_cross"] = mutation["compact_tree_cross_functional"]["relative_tree_cross"].replace("2*sqrt(2)", "sqrt(2)")
        self.assert_rejected(mutation)

    def test_rejects_packet_prefactor_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["compact_tree_cross_functional"]["fixture_probability"] = mutation["compact_tree_cross_functional"]["fixture_probability"].replace("25*sqrt(2)", "50*sqrt(2)")
        self.assert_rejected(mutation)

    def test_rejects_cell_matrix_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["box_to_packet_limit"]["connected_matrix"] = "B_ij=W_ij"
        self.assert_rejected(mutation)

    def test_rejects_double_sum_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["box_to_packet_limit"]["constant_kernel_fixture"][2]["matrix_element"] = "7/11"
        self.assert_rejected(mutation)

    def test_rejects_diagonal_only_substitution(self):
        mutation = copy.deepcopy(self.certificate)
        fixture = mutation["box_to_packet_limit"]["nonconstant_fixture"]
        fixture["matrix_element"] = fixture["diagonal_only_wrong_value"]
        self.assert_rejected(mutation)

    def test_rejects_single_mode_continuum_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["physical_interpretation"]["fixed_compact_packet_box_refinement"] = "ZERO_AS_1_OVER_V"
        self.assert_rejected(mutation)

    def test_rejects_all_time_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("uniform control of the secular limit T to infinity")
        self.assert_rejected(mutation)

    def test_rejects_complete_lambda6_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["physical_interpretation"]["complete_order_lambda6_probability"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_source_completion_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["physical_interpretation"]["active_loop_source_survival_completion"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_Eq19_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["physical_interpretation"]["general_Eq19"] = "PROVED"
        self.assert_rejected(mutation)

    def test_rejects_gravity_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["physical_interpretation"]["gravity_or_BV_BRST_transfer"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_Lorentzian_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["physical_interpretation"]["Lorentzian_causal_claim"] = "ESTABLISHED"
        self.assert_rejected(mutation)


if __name__ == "__main__":
    unittest.main()
