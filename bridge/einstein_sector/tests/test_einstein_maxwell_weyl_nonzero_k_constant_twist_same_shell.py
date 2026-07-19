from __future__ import annotations

import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_nonzero_k_constant_twist_same_shell import build


class NonzeroKConstantTwistSameShellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_exact_shell_scalars(self) -> None:
        scalars = self.value["flat_connection_Feynman_Hellmann"]["on_shell_action_Gram_scalars"]
        self.assertEqual(scalars["Einstein_minus_q"], "4*sqrt(2)*j*k*sqrt(lambda)")
        self.assertEqual(scalars["Einstein_plus_q"], "-4*sqrt(2)*j*k*sqrt(lambda)")
        self.assertEqual(scalars["extra_p"], "-2*j*k")

    def test_complete_multiplicity_kernel(self) -> None:
        theorem = self.value["kernel_theorem"]
        self.assertEqual(theorem["multiplicity_dimensions"], {"q_minus": 2, "q_plus": 2, "p": 4})
        self.assertEqual(theorem["kernel_dimension_per_positive_signed_momentum_fibre"], 8)
        self.assertIn("m_A=0", theorem["complete_same_shell_kernel"])

    def test_rest_travelling_contrast(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["rest_frame_spectator_contrast_exact"])
        self.assertTrue(classification["same_shell_kernel_exactly_axisymmetric_about_twist"])

    def test_neighboring_outputs_are_uniformly_invertible(self) -> None:
        theorem = self.value["neighboring_output_extension"]
        self.assertTrue(theorem["complete_neighboring_output_inverse"])
        self.assertTrue(theorem["channels"]["L=ell-1"]["all_generic_target_blocks_invertible"])
        self.assertTrue(theorem["channels"]["L=ell+1"]["all_generic_target_blocks_invertible"])
        self.assertTrue(theorem["channels"]["ell=2 exceptional L=1"]["all_exceptional_target_blocks_invertible"])

    def test_full_bounded_gate_remains_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["complete_bounded_second_order_equation_solved"])
        bounded = self.value["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]
        self.assertIn("OPEN", bounded["full_equation"])
        self.assertTrue(classification["complete_constant_twist_times_wave_bilinear_column_classified"])

    def test_causal_gate_fail_closed(self) -> None:
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
