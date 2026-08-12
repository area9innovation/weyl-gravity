"""Falsification tests for the BT projective Fejer packet detector."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_two_angle_fejer_packet_detector import CERT, verify


class TwoAngleFejerPacketDetectorTests(unittest.TestCase):
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

    def test_rejects_order_mutation(self):
        value = self.mutated()
        value["continuous_filter"]["order_N"] = 19
        self.reject(value)

    def test_rejects_derivative_order_mutation(self):
        value = self.mutated()
        value["continuous_filter"]["maximum_transverse_derivative_order"] = 36
        self.reject(value)

    def test_rejects_support_mutation(self):
        value = self.mutated()
        value["continuous_filter"]["kernel_Laurent_support"] = [-18, 18]
        self.reject(value)

    def test_rejects_rho_mutation(self):
        value = self.mutated()
        value["continuous_filter"]["rho_exact"] = "1/2"
        self.reject(value)

    def test_rejects_target_phase_mutation(self):
        value = self.mutated()
        value["continuous_filter"]["target_zeta_values"][1] = "(-7+23*i)/25"
        self.reject(value)

    def test_rejects_target_weight_mutation(self):
        value = self.mutated()
        value["continuous_filter"]["target_weights"][1] = "1"
        self.reject(value)

    def test_rejects_local_realization_removal(self):
        value = self.mutated()
        value["continuous_filter"]["local_density_realization"] = "abstract matrix"
        self.reject(value)

    def test_rejects_packet_zero_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["packet_zero_c_interval"][1] = "6/25"
        self.reject(value)

    def test_rejects_packet_one_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["packet_one_c_interval"][0] = "6/13"
        self.reject(value)

    def test_rejects_measure_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["measure"] = "dtheta"
        self.reject(value)

    def test_rejects_total_hash_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["exact_integral_receipts"]["total_norm_squared"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_packet_zero_hash_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["exact_integral_receipts"]["packet_zero_norm_squared"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_packet_one_hash_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["exact_integral_receipts"]["packet_one_norm_squared"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_leakage_hash_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["exact_integral_receipts"]["leakage_norm_squared"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_eta_hash_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["exact_integral_receipts"]["leakage_fraction_eta"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_eta_upper_bound_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["exact_integral_receipts"]["leakage_fraction_eta"]["upper_bound"] = "3/4000"
        self.reject(value)

    def test_rejects_digit_count_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["exact_integral_receipts"]["leakage_fraction_eta"]["numerator_digits"] -= 1
        self.reject(value)

    def test_rejects_decimal_display_mutation(self):
        value = self.mutated()
        value["packet_decomposition"]["exact_integral_receipts"]["leakage_fraction_eta"]["decimal"] = "0.0001"
        self.reject(value)

    def test_rejects_leakage_bound_promotion(self):
        value = self.mutated()
        value["packet_decomposition"]["leakage_bound"] = "eta=0"
        self.reject(value)

    def test_rejects_residual_deletion(self):
        value = self.mutated()
        value["residual_retaining_evolution"]["Hamiltonian"] = "H/G=|e><B|+|B><e|"
        self.reject(value)

    def test_rejects_exponential_substitution(self):
        value = self.mutated()
        value["residual_retaining_evolution"]["compressed_exponential_relation"] = "Pi U Pi=exp(-i Pi H Pi tau)"
        self.reject(value)

    def test_rejects_absorption_effect_mutation(self):
        value = self.mutated()
        value["residual_retaining_evolution"]["selected_absorption_effect"] = "E_absorb=P_B"
        self.reject(value)

    def test_rejects_pass_effect_mutation(self):
        value = self.mutated()
        value["residual_retaining_evolution"]["selected_pass_effect"] = "E_pass=P_D"
        self.reject(value)

    def test_rejects_exact_selectivity_promotion(self):
        value = self.mutated()
        value["disposition"]["exact_zero_width_two_angle_selectivity"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_complete_Hamiltonian_promotion(self):
        value = self.mutated()
        value["disposition"]["complete_local_scalar_detector_Hamiltonian"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_absolute_q8_promotion(self):
        value = self.mutated()
        value["disposition"]["absolute_q8_probability"] = "COMPUTED"
        self.reject(value)

    def test_rejects_relative_q8_transfer_boundary_removal(self):
        value = self.mutated()
        value["does_not_establish"] = [
            row for row in value["does_not_establish"]
            if "equal-weight two-mode effect" not in row
        ]
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

    def test_rejects_literature_boundary_removal(self):
        value = self.mutated()
        value["does_not_establish"] = [
            row for row in value["does_not_establish"] if row != "literature priority"
        ]
        self.reject(value)

    def test_rejects_input_hash_mutation(self):
        value = self.mutated()
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.reject(value)


if __name__ == "__main__":
    unittest.main()
