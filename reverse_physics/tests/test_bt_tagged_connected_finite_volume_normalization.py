import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_tagged_connected_finite_volume_normalization import CERT, verify


class TaggedConnectedFiniteVolumeNormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation):
        self.assertFalse(all(verify(mutation).values()))

    def test_all_independent_checks(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_CCR_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["common_finite_volume_spectator"]["public_cross_CCR"] = "[b_Omega,b_Upsilon^dagger]=E*delta_3"
        self.assert_rejected(mutation)

    def test_rejects_mode_norm_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["common_finite_volume_spectator"]["fixture_norm"] = "N_s=6*kappa*V/5"
        self.assert_rejected(mutation)

    def test_rejects_identity_normalization_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["common_finite_volume_spectator"]["disconnected_identity_factor"] = "N_s"
        self.assert_rejected(mutation)

    def test_rejects_connected_factor_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["common_finite_volume_spectator"]["connected_factor"] = "1"
        self.assert_rejected(mutation)

    def test_rejects_scale_covariance_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["scaled_finite_time_kernel"]["scale_covariance"] = "W_kappa(T)=w(kappa*T)/kappa"
        self.assert_rejected(mutation)

    def test_rejects_W_dimension_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["scaled_finite_time_kernel"]["mass_dimension"] = -1
        self.assert_rejected(mutation)

    def test_rejects_W_rate_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["scaled_finite_time_kernel"]["large_time_rate"] = "lim W/T=6/kappa"
        self.assert_rejected(mutation)

    def test_rejects_external_cross_factor_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["dimensionless_tree_cross_probability"]["box_normalized_external_jet_cross"] = "I_box^(6)=16*sqrt(2)*lambda^6*W_kappa(T)"
        self.assert_rejected(mutation)

    def test_rejects_relative_coefficient_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["dimensionless_tree_cross_probability"]["relative_tree_cross"] = "I_box/(24*lambda^4)=sqrt(2)*lambda^2*W/N_s"
        self.assert_rejected(mutation)

    def test_rejects_probability_coefficient_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["dimensionless_tree_cross_probability"]["tree_cross_contribution"] = mutation["dimensionless_tree_cross_probability"]["tree_cross_contribution"].replace("125*sqrt(2)", "124*sqrt(2)")
        self.assert_rejected(mutation)

    def test_rejects_thermodynamic_limit_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["limit_classification"]["fixed_finite_T_V_to_infinity"] = "q_cross^(6)->constant"
        self.assert_rejected(mutation)

    def test_rejects_large_time_rate_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["limit_classification"]["fixed_finite_V_T_to_infinity"] = "q_cross^(6)/T->0"
        self.assert_rejected(mutation)

    def test_rejects_relative_rate_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["limit_classification"]["large_time_relative_rate"] = "(q_cross/q_tag)/T->0"
        self.assert_rejected(mutation)

    def test_rejects_double_scaling_mutation(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["limit_classification"]["double_scaling_variable"] = "tau=T/V"
        self.assert_rejected(mutation)

    def test_rejects_compact_packet_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["compact_packet_replacement"] = "CONSTRUCTED"
        self.assert_rejected(mutation)

    def test_rejects_complete_lambda6_promotion(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["interpretation"]["complete_order_lambda6_probability"] = "COMPUTED"
        self.assert_rejected(mutation)

    def test_rejects_all_time_decoupling_boundary_removal(self):
        mutation = copy.deepcopy(self.certificate)
        mutation["does_not_establish"].remove("all-time decoupling from the fixed-time V-to-infinity limit")
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
