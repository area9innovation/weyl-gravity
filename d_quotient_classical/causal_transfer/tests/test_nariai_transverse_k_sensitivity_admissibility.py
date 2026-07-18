import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_k_sensitivity_admissibility import exact_data


class TransverseKSensitivityAdmissibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = exact_data()

    def test_formal_screen(self):
        screen = self.data["formal_screen"]
        self.assertEqual(screen["basis_dimension"], 180)
        self.assertEqual(screen["nonzero_direction_count"], 23)
        self.assertTrue(screen["all_nonzero_directions_first_order"])

    def test_action_derived_gate(self):
        gate = self.data["action_derived_admissibility"]
        self.assertEqual(gate["authoritative_delta_K_nonzero_coefficients"], 0)
        self.assertEqual(gate["authoritative_delta_K_orders"], [])
        self.assertFalse(gate["formal_sensitive_direction_admissible"])

    def test_scope(self):
        self.assertTrue(self.data["interpretation"]["obstruction_formally_K_sensitive"])
        self.assertFalse(self.data["interpretation"]["repair_within_action_derived_target_complex"])
        self.assertFalse(self.data["interpretation"]["complete_coupled_SDR_obstructed"])


if __name__ == "__main__":
    unittest.main()
