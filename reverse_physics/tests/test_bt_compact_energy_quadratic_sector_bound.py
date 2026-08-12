"""Falsification tests for the compact-energy BT quadratic-sector bound."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_compact_energy_quadratic_sector_bound import CERT, verify


class CompactEnergyQuadraticSectorBoundTests(unittest.TestCase):
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

    def test_rejects_source_commit(self):
        self.mutate("provenance", "source_commit", "0" * 40)

    def test_rejects_lifecycle_promotion(self):
        value = self.mutated()
        value["lifecycle_state"] = "LORENTZIAN_CERTIFIED"
        self.reject(value)

    def test_rejects_dependency_promotion(self):
        value = self.mutated()
        value["dependency_tags"].append("LORENTZIAN-CAUSAL")
        self.reject(value)

    def test_rejects_producer_check_count(self):
        value = self.mutated()
        value["checks"]["total"] = 30
        value["checks"]["passed"] = 30
        self.reject(value)

    def test_rejects_sigma(self):
        self.mutate("desired_pair_lower_bound", "sigma_over_M0", "1/40000")

    def test_rejects_Gaussian_core(self):
        self.mutate("desired_pair_lower_bound", "Gaussian_core", "||P-P0||<=5*sigma")

    def test_rejects_angular_exact(self):
        value = self.mutated()
        value["desired_pair_lower_bound"]["angular_pi_coefficient_lower"]["exact"] = "1/2"
        self.reject(value)

    def test_rejects_angular_hash(self):
        value = self.mutated()
        value["desired_pair_lower_bound"]["angular_pi_coefficient_lower"]["canonical_sha256"] = "0" * 64
        self.reject(value)

    def test_rejects_angular_bound(self):
        self.mutate("desired_pair_lower_bound", "angular_pi_coefficient_bound", "t>0")

    def test_rejects_ball_integral(self):
        self.mutate("desired_pair_lower_bound", "four_ball_integral", "pi^2")

    def test_rejects_desired_norm(self):
        self.mutate("desired_pair_lower_bound", "norm_lower", "||w||^2>0")

    def test_rejects_desired_status(self):
        self.mutate("desired_pair_lower_bound", "status", "ASSERTED")

    def test_rejects_density_formula(self):
        self.mutate("off_shell_local_density", "density", ":F(i*partial_1/M0)phi(x_1)phi(x_2):")

    def test_rejects_jet_order(self):
        self.mutate("off_shell_local_density", "jet_order", 36)

    def test_rejects_pair_symbol(self):
        self.mutate("off_shell_local_density", "pair_annihilation_symbol", "F((k1+k2)/M0)")

    def test_rejects_number_symbol(self):
        self.mutate("off_shell_local_density", "number_scattering_symbol", "F((k-k_prime)/M0)")

    def test_rejects_pair_transfer(self):
        self.mutate("off_shell_local_density", "pair_Fourier_transfer", "k1-k2")

    def test_rejects_number_transfer(self):
        self.mutate("off_shell_local_density", "number_Fourier_transfer", "k+k_prime")

    def test_rejects_energy_band(self):
        self.mutate("number_operator_bound", "energy_band_over_M0", ["1/5", "4/5"])

    def test_rejects_energy_measure(self):
        self.mutate("number_operator_bound", "energy_band_measure", "mu(K)=pi*M0^2")

    def test_rejects_number_kernel(self):
        self.mutate("number_operator_bound", "kernel", "N=0")

    def test_rejects_polynomial_bound(self):
        self.mutate("number_operator_bound", "polynomial_bound", "|F|<=A0")

    def test_rejects_Hilbert_Schmidt_formula(self):
        self.mutate("number_operator_bound", "Hilbert_Schmidt_bound", "||N||_HS^2=0")

    def test_rejects_number_prefactor(self):
        self.mutate("number_operator_bound", "relative_prefactor_dyadic_bound", "prefactor<2^152")

    def test_rejects_number_relative_bound(self):
        self.mutate("number_operator_bound", "squared_relative_norm_bound", "||N||=0")

    def test_rejects_number_status(self):
        self.mutate("number_operator_bound", "status", "POINTWISE_ONLY")

    def test_rejects_wrong_kernel(self):
        self.mutate("wrong_sign_pair_bound", "kernel", "w_minus=0")

    def test_rejects_wrong_radial_domain(self):
        self.mutate("wrong_sign_pair_bound", "radial_domain", "R>=0")

    def test_rejects_wrong_decay(self):
        self.mutate("wrong_sign_pair_bound", "decay_coefficient", "1")

    def test_rejects_wrong_exponent(self):
        self.mutate("wrong_sign_pair_bound", "tail_exponent", "2500000000")

    def test_rejects_wrong_prefactor(self):
        self.mutate("wrong_sign_pair_bound", "relative_prefactor_dyadic_bound", "prefactor<2^46")

    def test_rejects_wrong_relative_bound(self):
        self.mutate("wrong_sign_pair_bound", "squared_relative_norm_bound", "||w_minus||=0")

    def test_rejects_wrong_status(self):
        self.mutate("wrong_sign_pair_bound", "status", "POINTWISE_ONLY")

    def test_rejects_desired_block(self):
        self.mutate("complete_first_Dyson_bound", "desired_block", "A_pair=0")

    def test_rejects_undesired_block_omission(self):
        value = self.mutated()
        value["complete_first_Dyson_bound"]["undesired_blocks"][0] = "none"
        self.reject(value)

    def test_rejects_complete_norm(self):
        self.mutate("complete_first_Dyson_bound", "relative_operator_norm", "zero")

    def test_rejects_click_error(self):
        self.mutate("complete_first_Dyson_bound", "leading_click_effect_error", "zero")

    def test_rejects_complete_status(self):
        self.mutate("complete_first_Dyson_bound", "status", "ALL_ORDERS")

    def test_rejects_unrestricted_energy_promotion(self):
        value = self.mutated()
        value["disposition"]["unrestricted_energy_number_operator"] = "COMPUTED"
        self.reject(value)

    def test_rejects_higher_Dyson_promotion(self):
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
        value["does_not_establish"] = [
            row for row in value["does_not_establish"] if row != "literature priority"
        ]
        self.reject(value)


if __name__ == "__main__":
    unittest.main()
