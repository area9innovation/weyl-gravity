"""Falsification tests for the finite two-angle BT apparatus Hamiltonian."""
import copy
import json
import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "reverse_physics"))
from verify_bt_two_angle_finite_apparatus_hamiltonian import CERT, verify


class TwoAngleFiniteApparatusHamiltonianTests(unittest.TestCase):
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

    def test_rejects_carrier_dimension_mutation(self):
        value = self.mutated()
        value["apparatus_carrier"]["combined_dimension"] = 6
        self.reject(value)

    def test_rejects_phase_projector_mutation(self):
        value = self.mutated()
        value["phase_selection"]["P_minus"][0][1] = "0"
        self.reject(value)

    def test_rejects_phase_shifter_mutation(self):
        value = self.mutated()
        value["phase_selection"]["phase_shifter"] = "I"
        self.reject(value)

    def test_rejects_phase_conjugation_mutation(self):
        value = self.mutated()
        value["phase_selection"]["conjugation"] = "P_minus(phi)=P_plus(0)"
        self.reject(value)

    def test_rejects_Hamiltonian_mutation(self):
        value = self.mutated()
        value["finite_Hamiltonian"]["interaction"] = "H_int=0"
        self.reject(value)

    def test_rejects_self_adjoint_promotion_mutation(self):
        value = self.mutated()
        value["finite_Hamiltonian"]["self_adjoint"] = False
        self.reject(value)

    def test_rejects_spectral_square_mutation(self):
        value = self.mutated()
        value["finite_Hamiltonian"]["spectral_square"] = "H^2=0"
        self.reject(value)

    def test_rejects_click_Kraus_mutation(self):
        value = self.mutated()
        value["derived_instrument"]["K_click"] = "P_plus"
        self.reject(value)

    def test_rejects_no_click_Kraus_mutation(self):
        value = self.mutated()
        value["derived_instrument"]["K_no"] = "0"
        self.reject(value)

    def test_rejects_click_effect_mutation(self):
        value = self.mutated()
        value["derived_instrument"]["E_click"] = "I"
        self.reject(value)

    def test_rejects_no_click_effect_mutation(self):
        value = self.mutated()
        value["derived_instrument"]["E_no"] = "0"
        self.reject(value)

    def test_rejects_epsilon_selection_mutation(self):
        value = self.mutated()
        value["derived_instrument"]["epsilon_selection"] = "epsilon=g*tau"
        self.reject(value)

    def test_rejects_completeness_mutation(self):
        value = self.mutated()
        value["derived_instrument"]["completeness"] = "K0^dagger K0=I"
        self.reject(value)

    def test_rejects_calibrated_setting_mutation(self):
        value = self.mutated()
        value["phase_calibration"]["calibrated_setting"] = "phi=0"
        self.reject(value)

    def test_rejects_fixed_point_mutation(self):
        value = self.mutated()
        value["phase_calibration"]["calibrated_fixed_point"] = "E_click X2=0"
        self.reject(value)

    def test_rejects_mismatch_response_mutation(self):
        value = self.mutated()
        value["phase_calibration"]["leading_click_probability"] = "2*|x2|^2"
        self.reject(value)

    def test_rejects_q6_transport_mutation(self):
        value = self.mutated()
        value["transported_BT_coefficients"]["through_q6"] = "q=0"
        self.reject(value)

    def test_rejects_q8_sign_mutation(self):
        value = self.mutated()
        value["transported_BT_coefficients"]["relative_q8"] = "q8[apparatus]-q8[recorded]=+variance"
        self.reject(value)

    def test_rejects_absolute_q8_promotion(self):
        value = self.mutated()
        value["transported_BT_coefficients"]["absolute_q8_status"] = "COMPUTED"
        self.reject(value)

    def test_rejects_fixture_click_Kraus_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["K_click"][0][0] = "3/5"
        self.reject(value)

    def test_rejects_fixture_effect_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["E_no"][0][0] = "9/25"
        self.reject(value)

    def test_rejects_fixture_epsilon_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["epsilon"] = "15/25"
        self.reject(value)

    def test_rejects_fixture_mismatch_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["quarter_turn_mismatch_probability_for_unit_x2"] = "33/25"
        self.reject(value)

    def test_rejects_fixture_q8_shift_mutation(self):
        value = self.mutated()
        value["exact_fixture"]["q8_shift"] = "8/25"
        self.reject(value)

    def test_rejects_public_BT_promotion(self):
        value = self.mutated()
        value["physical_affiliation"]["public_closed_system_BT_Hamiltonian_prediction"] = "ESTABLISHED"
        self.reject(value)

    def test_rejects_spacetime_local_promotion(self):
        value = self.mutated()
        value["physical_affiliation"]["spacetime_local_detector_coupling"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_continuum_promotion(self):
        value = self.mutated()
        value["physical_affiliation"]["continuum_angle_limit"] = "CONSTRUCTED"
        self.reject(value)

    def test_rejects_Eq19_boundary_removal(self):
        value = self.mutated()
        value["does_not_establish"] = [
            row for row in value["does_not_establish"] if "Eq. (19)" not in row
        ]
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
