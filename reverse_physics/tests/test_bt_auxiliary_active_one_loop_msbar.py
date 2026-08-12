import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_auxiliary_active_one_loop_msbar import CERT, verify


class AuxiliaryActiveOneLoopMSbarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_lifecycle_demotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["lifecycle_state"] = "CLASSIFIED"
        self.assert_rejected(mutation)

    def test_rejects_species_weight_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["species_enumeration"]["bubble_weights"][0]["s"] = 4
        self.assert_rejected(mutation)

    def test_rejects_channel_sum_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["species_enumeration"]["channel_column_sums"]["t"] = 18
        self.assert_rejected(mutation)

    def test_rejects_tree_norm_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["species_enumeration"]["tree_norm"] = 20
        self.assert_rejected(mutation)

    def test_rejects_bubble_constant_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["msbar_bubble"]["real_bubble"] = "B_X=L_X+1"
        self.assert_rejected(mutation)

    def test_rejects_three_channel_constant_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["msbar_bubble"]["three_channel_sum"] = "B_s+B_t+B_u=L_s+L_t+L_u+3"
        self.assert_rejected(mutation)

    def test_rejects_full_density_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["active_virtual_probability"]["complete_msbar_density"] = "wrong"
        self.assert_rejected(mutation)

    def test_rejects_hard_log_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["active_virtual_probability"]["logarithmic_part"] = "wrong"
        self.assert_rejected(mutation)

    def test_rejects_fixture_constant_omission(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["tagged_fixture"]["local_click"] = "q_active proportional to L_*"
        self.assert_rejected(mutation)

    def test_rejects_finite_duration_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["finite_duration_BT_Dyson_affiliation"] = "PROVED"
        self.assert_rejected(mutation)

    def test_rejects_complete_q6_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["complete_tagged_q6_probability"] = "COMPUTED"
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
