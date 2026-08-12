"""Falsification tests for the invariant fixed-P BT sphere detector."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_fixed_p_two_sphere_packet_detector import CERT, verify


class FixedPTwoSpherePacketDetectorTests(unittest.TestCase):
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

    def test_rejects_input_hash_mutation(self):
        value = self.mutated()
        value["provenance"]["inputs"][0]["sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_dependency_promotion(self):
        value = self.mutated()
        value["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.reject(value)

    def test_rejects_lifecycle_promotion(self):
        value = self.mutated()
        value["lifecycle_state"] = "LORENTZIAN_CERTIFIED"
        self.reject(value)

    def test_rejects_total_momentum_mutation(self):
        value = self.mutated()
        value["fixed_P_shell"]["lab_total_momentum_over_kappa"][1] = "-7/5"
        self.reject(value)

    def test_rejects_invariant_mass_mutation(self):
        value = self.mutated()
        value["fixed_P_shell"]["invariant_mass_squared_over_kappa_squared"] = "63/25"
        self.reject(value)

    def test_rejects_boost_mutation(self):
        value = self.mutated()
        value["fixed_P_shell"]["lab_boost"] = "beta_x=-2/5, gamma=5/4"
        self.reject(value)

    def test_rejects_dc_as_invariant_measure(self):
        value = self.mutated()
        value["fixed_P_shell"]["measure"] = "dc"
        self.reject(value)

    def test_rejects_equator_removal(self):
        value = self.mutated()
        value["fixed_P_shell"]["previous_family"] = "complete sphere"
        self.reject(value)

    def test_rejects_order_mutation(self):
        value = self.mutated()
        value["homogeneous_local_filter"]["order_N"] = 19
        self.reject(value)

    def test_rejects_derivative_order_mutation(self):
        value = self.mutated()
        value["homogeneous_local_filter"]["maximum_derivative_order"] = 36
        self.reject(value)

    def test_rejects_rho_mutation(self):
        value = self.mutated()
        value["homogeneous_local_filter"]["rho_exact"] = "1/2"
        self.reject(value)

    def test_rejects_sphere_filter_mutation(self):
        value = self.mutated()
        value["homogeneous_local_filter"]["sphere_filter"] = "F(n)=p(phi)"
        self.reject(value)

    def test_rejects_mode_polynomial_removal(self):
        value = self.mutated()
        value["homogeneous_local_filter"]["mode_polynomial"] = "abstract lift"
        self.reject(value)

    def test_rejects_local_realization_removal(self):
        value = self.mutated()
        value["homogeneous_local_filter"]["local_density_realization"] = "abstract matrix"
        self.reject(value)

    def test_rejects_antipodal_promotion(self):
        value = self.mutated()
        value["homogeneous_local_filter"]["antipodal_property"] = "not checked"
        self.reject(value)

    def test_rejects_phi_measure_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["azimuthal_measure"] = "dc"
        self.reject(value)

    def test_rejects_phi_bin_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["target_one_phi_interval"][0] = "pi/5"
        self.reject(value)

    def test_rejects_latitude_band_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["latitude_band"][1] = "2/3"
        self.reject(value)

    def test_rejects_sqrt_bound_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["radical_bounds"]["sqrt2_lower"] = "3/2"
        self.reject(value)

    def test_rejects_pi_bound_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["radical_bounds"]["pi_upper"] = "3"
        self.reject(value)

    def test_rejects_equatorial_hash_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["equatorial_leakage_fraction"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_equatorial_coefficient_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["equatorial_total_norm"]["coefficients"][0] = "1"
        self.reject(value)

    def test_rejects_latitude_hash_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["latitude_leakage_fraction"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_latitude_decimal_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["latitude_leakage_fraction"]["decimal"] = "0.1"
        self.reject(value)

    def test_rejects_sphere_total_hash_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["sphere_total_norm"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_sphere_packet_hash_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["sphere_target_zero_norm"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_sphere_leakage_hash_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["sphere_leakage_norm"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_sphere_eta_bound_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["sphere_leakage_fraction"]["upper_bound"] = "1/2"
        self.reject(value)

    def test_rejects_sphere_eta_decimal_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["sphere_leakage_fraction"]["decimal"] = "0.0001"
        self.reject(value)

    def test_rejects_leakage_claim_mutation(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["leakage_bound"] = "eta_sphere=0"
        self.reject(value)

    def test_rejects_residual_deletion_from_packet(self):
        value = self.mutated()
        value["sphere_packet_decomposition"]["complete_direction"] = "v=B"
        self.reject(value)

    def test_rejects_residual_deletion_from_Hamiltonian(self):
        value = self.mutated()
        value["residual_retaining_evolution"]["Hamiltonian"] = "H/G=|e><B|+|B><e|"
        self.reject(value)

    def test_rejects_absorption_effect_mutation(self):
        value = self.mutated()
        value["residual_retaining_evolution"]["selected_absorption_effect"] = "E_absorb=P_B"
        self.reject(value)

    def test_rejects_exponential_substitution(self):
        value = self.mutated()
        value["residual_retaining_evolution"]["compressed_exponential_relation"] = "Pi U Pi=exp(-i Pi H Pi tau)"
        self.reject(value)

    def test_rejects_bandwidth_promotion(self):
        value = self.mutated()
        value["disposition"]["energy_and_total_momentum_bandwidth"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_complete_Hamiltonian_promotion(self):
        value = self.mutated()
        value["disposition"]["complete_local_scalar_detector_Hamiltonian"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_absolute_q8_promotion(self):
        value = self.mutated()
        value["disposition"]["absolute_q8_probability"] = "COMPUTED"
        self.reject(value)

    def test_rejects_relative_q8_boundary_removal(self):
        value = self.mutated()
        value["does_not_establish"] = [row for row in value["does_not_establish"] if "relative q8" not in row]
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
