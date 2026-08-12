"""Falsification tests for the BT Schwartz four-momentum packet response."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_schwartz_four_momentum_packet_response import CERT, verify


class SchwartzFourMomentumPacketResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(CERT, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def mutated(self):
        return copy.deepcopy(self.certificate)

    def reject(self, value):
        self.assertFalse(all(verify(value).values()))

    def mutate(self, section, field, value):
        payload = self.mutated()
        payload[section][field] = value
        self.reject(payload)

    def test_independent_verifier(self):
        self.assertTrue(all(verify(self.certificate).values()))

    def test_rejects_input_hash(self):
        value = self.mutated()
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_lifecycle_promotion(self):
        value = self.mutated()
        value["lifecycle_state"] = "LORENTZIAN_CERTIFIED"
        self.reject(value)

    def test_rejects_dependency_promotion(self):
        value = self.mutated()
        value["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.reject(value)

    def test_rejects_target_P0(self):
        self.mutate("Schwartz_local_vertex", "target_P0_COM_over_kappa", ["2", "0", "0", "0"])

    def test_rejects_epsilon(self):
        self.mutate("Schwartz_local_vertex", "epsilon", "1/1000")

    def test_rejects_sigma_M0(self):
        self.mutate("Schwartz_local_vertex", "sigma_over_M0", "1/40000")

    def test_rejects_sigma_kappa(self):
        self.mutate("Schwartz_local_vertex", "sigma_over_kappa", "1/30000")

    def test_rejects_envelope(self):
        self.mutate("Schwartz_local_vertex", "squared_Fourier_envelope", "compact support")

    def test_rejects_compact_support_promotion(self):
        self.mutate("Schwartz_local_vertex", "support_status", "COMPACT")

    def test_rejects_density_order(self):
        self.mutate("Schwartz_local_vertex", "local_density_order", 36)

    def test_rejects_core_radius(self):
        self.mutate("concentration_bound", "core_radius_over_M0", "1/1000")

    def test_rejects_sigma_count(self):
        self.mutate("concentration_bound", "core_radius_in_sigma", 4)

    def test_rejects_coefficient_bound(self):
        self.mutate("concentration_bound", "coefficient_l1_bound", "2")

    def test_rejects_phase_bound(self):
        self.mutate("concentration_bound", "phase_derivative_l1_bound", "1")

    def test_rejects_gradient_bound(self):
        self.mutate("concentration_bound", "gradient_bound", "1")

    def test_rejects_gamma_bound(self):
        self.mutate("concentration_bound", "gamma_minus_one_bound", "0")

    def test_rejects_filter_error(self):
        self.mutate("concentration_bound", "filter_sup_difference_bound", "0")

    def test_rejects_core_ratio_hash(self):
        value = self.mutated()
        value["concentration_bound"]["core_angular_leakage_fraction"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_core_ratio_upper(self):
        value = self.mutated()
        value["concentration_bound"]["core_angular_leakage_fraction"]["upper_bound"] = "1/2"
        self.reject(value)

    def test_rejects_core_ratio_decimal(self):
        value = self.mutated()
        value["concentration_bound"]["core_angular_leakage_fraction"]["upper_decimal"] = "0.1"
        self.reject(value)

    def test_rejects_decay(self):
        self.mutate("concentration_bound", "tail_decay_coefficient", "1/2")

    def test_rejects_tail_terms(self):
        self.mutate("concentration_bound", "tail_exponential_partial_sum_terms", 74)

    def test_rejects_e_terms(self):
        self.mutate("concentration_bound", "unit_ball_e_partial_sum_terms", 19)

    def test_rejects_tail_hash(self):
        value = self.mutated()
        value["concentration_bound"]["four_momentum_tail_fraction_upper"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_tail_decimal(self):
        value = self.mutated()
        value["concentration_bound"]["four_momentum_tail_fraction_upper"]["decimal"] = "0.1"
        self.reject(value)

    def test_rejects_complete_hash(self):
        value = self.mutated()
        value["concentration_bound"]["complete_leakage_fraction_upper"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_complete_exact(self):
        value = self.mutated()
        value["concentration_bound"]["complete_leakage_fraction_upper"]["exact"] = "1/2"
        self.reject(value)

    def test_rejects_complete_bound(self):
        self.mutate("concentration_bound", "bound", "eta_complete=0")

    def test_rejects_number_transfer(self):
        self.mutate("spectral_separation", "number_scattering_transfer", "timelike")

    def test_rejects_number_distance(self):
        self.mutate("spectral_separation", "number_cone_distance_squared_over_M0_squared", "1/3")

    def test_rejects_number_suppression(self):
        self.mutate("spectral_separation", "number_squared_envelope_bound", "1")

    def test_rejects_wrong_distance(self):
        self.mutate("spectral_separation", "wrong_sign_distance_squared_over_M0_squared", "1/2")

    def test_rejects_wrong_suppression(self):
        self.mutate("spectral_separation", "wrong_sign_squared_envelope_bound", "1")

    def test_rejects_operator_promotion(self):
        self.mutate("spectral_separation", "meaning", "complete operator-norm bound")

    def test_rejects_normalized_mode(self):
        self.mutate("leading_packet_instrument", "normalized_mode", "v=w")

    def test_rejects_strength(self):
        self.mutate("leading_packet_instrument", "strength", "zeta=1")

    def test_rejects_click_effect(self):
        self.mutate("leading_packet_instrument", "click_effect", "E_click=I")

    def test_rejects_no_click_effect(self):
        self.mutate("leading_packet_instrument", "no_click_effect", "E_no=0")

    def test_rejects_positivity_domain(self):
        self.mutate("leading_packet_instrument", "positivity_domain", "all zeta")

    def test_rejects_capture(self):
        self.mutate("leading_packet_instrument", "selected_packet_capture", "zero")

    def test_rejects_compact_switching_disposition(self):
        value = self.mutated()
        value["disposition"]["compact_spacetime_switching"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_number_operator_promotion(self):
        value = self.mutated()
        value["disposition"]["complete_number_scattering_operator_bound"] = "COMPUTED"
        self.reject(value)

    def test_rejects_Dyson_promotion(self):
        value = self.mutated()
        value["disposition"]["complete_time_ordered_Dyson_evolution"] = "COMPUTED"
        self.reject(value)

    def test_rejects_absolute_q8_promotion(self):
        value = self.mutated()
        value["disposition"]["absolute_q8_probability"] = "COMPUTED"
        self.reject(value)

    def test_rejects_Eq19_promotion(self):
        value = self.mutated()
        value["disposition"]["general_Eq19"] = "PROVED"
        self.reject(value)

    def test_rejects_gravity_promotion(self):
        value = self.mutated()
        value["disposition"]["gravity_or_metric_BV_BRST_transfer"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_Lorentzian_promotion(self):
        value = self.mutated()
        value["disposition"]["Lorentzian_causal_claim"] = "ESTABLISHED"
        self.reject(value)

    def test_rejects_literature_boundary_removal(self):
        value = self.mutated()
        value["does_not_establish"] = [row for row in value["does_not_establish"] if row != "literature priority"]
        self.reject(value)


if __name__ == "__main__":
    unittest.main()
