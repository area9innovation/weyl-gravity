"""Falsification tests for BT local two-angle detector compression."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_two_angle_local_detector_compression import CERT, verify


class TwoAngleLocalDetectorCompressionTests(unittest.TestCase):
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

    def test_rejects_common_momentum_mutation(self):
        value = self.mutated()
        value["rational_pair_matrix_elements"]["common_total_four_momentum"][1] = "-7/5"
        self.reject(value)

    def test_rejects_derivative_weight_mutation(self):
        value = self.mutated()
        value["rational_pair_matrix_elements"]["normalized_derivative_weights"][1] = "143/625"
        self.reject(value)

    def test_rejects_contrast_density_mutation(self):
        value = self.mutated()
        value["rational_pair_matrix_elements"]["D_minus"] = ":phi^2:"
        self.reject(value)

    def test_rejects_contrast_weight_mutation(self):
        value = self.mutated()
        value["rational_pair_matrix_elements"]["D_minus_weights"][1] = "1"
        self.reject(value)

    def test_rejects_alpha_mutation(self):
        value = self.mutated()
        value["phase_quadrature_synthesis"]["alpha"] = "0"
        self.reject(value)

    def test_rejects_beta_mutation(self):
        value = self.mutated()
        value["phase_quadrature_synthesis"]["beta"] = "0"
        self.reject(value)

    def test_rejects_quadrature_interaction_mutation(self):
        value = self.mutated()
        value["phase_quadrature_synthesis"]["Hermitian_two_quadrature_interaction"] = "H=0"
        self.reject(value)

    def test_rejects_compressed_Hamiltonian_mutation(self):
        value = self.mutated()
        value["selected_sector_compression"]["Hamiltonian_over_G"][1][2] = "0"
        self.reject(value)

    def test_rejects_pass_effect_mutation(self):
        value = self.mutated()
        value["selected_sector_compression"]["E_pass"] = "I"
        self.reject(value)

    def test_rejects_absorption_effect_mutation(self):
        value = self.mutated()
        value["selected_sector_compression"]["E_absorb"] = "0"
        self.reject(value)

    def test_rejects_vandermonde_rank_mutation(self):
        value = self.mutated()
        value["continuum_locality_no_go"]["vandermonde_witnesses"][3]["rank"] = 6
        self.reject(value)

    def test_rejects_vandermonde_determinant_mutation(self):
        value = self.mutated()
        value["continuum_locality_no_go"]["vandermonde_witnesses"][2]["determinant_nonzero"] = False
        self.reject(value)

    def test_rejects_finite_Laurent_boundary_removal(self):
        value = self.mutated()
        value["continuum_locality_no_go"]["finite_derivative_fact"] = "arbitrary function"
        self.reject(value)

    def test_rejects_root_argument_mutation(self):
        value = self.mutated()
        value["continuum_locality_no_go"]["root_argument"] = "two roots imply zero"
        self.reject(value)

    def test_rejects_no_go_promotion(self):
        value = self.mutated()
        value["continuum_locality_no_go"]["status"] = "EXACT_SELECTIVITY_CONSTRUCTED"
        self.reject(value)

    def test_rejects_full_invariance_promotion(self):
        value = self.mutated()
        value["leakage_boundary"]["selected_sector_invariance_under_full_local_Hamiltonian"] = "ESTABLISHED"
        self.reject(value)

    def test_rejects_full_exponential_promotion(self):
        value = self.mutated()
        value["leakage_boundary"]["full_compressed_exponential_identity"] = "ESTABLISHED"
        self.reject(value)

    def test_rejects_disposition_selectivity_promotion(self):
        value = self.mutated()
        value["disposition"]["exact_continuum_two_angle_local_selectivity"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_full_detector_promotion(self):
        value = self.mutated()
        value["disposition"]["full_local_detector_evolution"] = "CONSTRUCTED"
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
