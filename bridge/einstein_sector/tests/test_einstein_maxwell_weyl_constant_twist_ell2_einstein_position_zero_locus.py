"""Tests for both ell=2 Einstein twist-position kernels."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_einstein_position_zero_locus import OUTPUT, build


class ConstantTwistEll2EinsteinPositionZeroLocusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_both_shell_matrices_are_equal_and_invertible(self) -> None:
        theorem = self.value["projection_theorem"]
        self.assertEqual(theorem["minus_position_matrix"], theorem["plus_position_matrix"])
        self.assertEqual(theorem["matrix_determinant"], "-93312/25")

    def test_each_shell_kernel_is_axisymmetric(self) -> None:
        theorem = self.value["projection_theorem"]
        self.assertEqual(theorem["each_shell_operator_rank"], 8)
        self.assertEqual(theorem["each_shell_kernel_positive_frequency_complex_dimension"], 2)
        self.assertEqual(theorem["each_shell_kernel"], "V_(m_A=0) tensor C^2_parity")

    def test_combined_q_primary_kernel_has_dimension_four(self) -> None:
        theorem = self.value["projection_theorem"]
        self.assertEqual(theorem["combined_q_primary_ambient_positive_frequency_complex_dimension"], 20)
        self.assertEqual(theorem["combined_q_primary_kernel_positive_frequency_complex_dimension"], 4)

    def test_scope_remains_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["simultaneous_moment_and_all_branch_resonance_zero_locus_classified"])
        self.assertFalse(classification["full_second_order_equation_solved"])


if __name__ == "__main__":
    unittest.main()
