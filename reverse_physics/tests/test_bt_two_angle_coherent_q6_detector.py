"""Falsification tests for the off-diagonal two-angle BT q6 detector."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_two_angle_coherent_q6_detector import CERT, verify


class TwoAngleCoherentQ6DetectorTests(unittest.TestCase):
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

    def test_rejects_leading_vector_mutation(self):
        value = self.mutated()
        value["two_angle_carrier"]["leading_angle_vector"] = "X2=x2*(1,-1)"
        self.reject(value)

    def test_rejects_cell_probability_mutation(self):
        value = self.mutated()
        value["two_angle_carrier"]["cell_probability"] = "q=0"
        self.reject(value)

    def test_rejects_rational_angle_mutation(self):
        value = self.mutated()
        value["rational_two_mode_fixture"]["c_values"][1] = "4/5"
        self.reject(value)

    def test_rejects_rational_momentum_mutation(self):
        value = self.mutated()
        value["rational_two_mode_fixture"]["outgoing"][1]["k1"][3] = "17/25"
        self.reject(value)

    def test_rejects_rational_t_mutation(self):
        value = self.mutated()
        value["rational_two_mode_fixture"]["outgoing"][1]["t"] = "-32/25"
        self.reject(value)

    def test_rejects_Pplus_mutation(self):
        value = self.mutated()
        value["off_diagonal_effect"]["P_plus"][0][1] = "0"
        self.reject(value)

    def test_rejects_Pminus_mutation(self):
        value = self.mutated()
        value["off_diagonal_effect"]["P_minus"][1][0] = "1/2"
        self.reject(value)

    def test_rejects_effect_diagonal_mutation(self):
        value = self.mutated()
        value["off_diagonal_effect"]["E_epsilon"][0][0] = "1"
        self.reject(value)

    def test_rejects_effect_off_diagonal_mutation(self):
        value = self.mutated()
        value["off_diagonal_effect"]["E_epsilon"][0][1] = "0"
        self.reject(value)

    def test_rejects_complement_mutation(self):
        value = self.mutated()
        value["off_diagonal_effect"]["E_no"][0][1] = "epsilon/2"
        self.reject(value)

    def test_rejects_spectrum_mutation(self):
        value = self.mutated()
        value["off_diagonal_effect"]["spectrum"] = ["1", "1+epsilon"]
        self.reject(value)

    def test_rejects_epsilon_domain_mutation(self):
        value = self.mutated()
        value["off_diagonal_effect"]["domain"] = "epsilon>1"
        self.reject(value)

    def test_rejects_relative_average_mutation(self):
        value = self.mutated()
        value["coherent_probability_through_lambda6"]["relative_coefficient"] = "R6_pair=R6(c1)"
        self.reject(value)

    def test_rejects_probability_mutation(self):
        value = self.mutated()
        value["coherent_probability_through_lambda6"]["probability"] = "q=q4"
        self.reject(value)

    def test_rejects_epsilon_dependence_mutation(self):
        value = self.mutated()
        value["coherent_probability_through_lambda6"]["epsilon_dependence"] = "NONZERO_AT_LAMBDA6"
        self.reject(value)

    def test_rejects_uniform_bound_mutation(self):
        value = self.mutated()
        value["coherent_probability_through_lambda6"]["uniform_bound"] = "|R6_pair|=infinity"
        self.reject(value)

    def test_rejects_q8_order_promotion(self):
        value = self.mutated()
        value["first_detector_sensitive_order"]["order"] = "lambda6"
        self.reject(value)

    def test_rejects_q8_variance_sign_mutation(self):
        value = self.mutated()
        value["first_detector_sensitive_order"]["difference"] = "+(epsilon/2)*||Y1-Y2||^2"
        self.reject(value)

    def test_rejects_q8_fixture_mutation(self):
        value = self.mutated()
        value["first_detector_sensitive_order"]["fixture"]["coherent_norm"] = "59/5"
        self.reject(value)

    def test_rejects_full_q8_promotion(self):
        value = self.mutated()
        value["first_detector_sensitive_order"]["full_q8_status"] = "COMPUTED"
        self.reject(value)

    def test_rejects_dynamical_selection_promotion(self):
        value = self.mutated()
        value["disposition"]["BT_dynamical_detector_selection"] = "ESTABLISHED"
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
