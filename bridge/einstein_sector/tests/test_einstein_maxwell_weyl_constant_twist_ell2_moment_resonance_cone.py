"""Tests for the ell=2 constant-twist moment/resonance cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_moment_resonance_cone import OUTPUT, build


class ConstantTwistEll2MomentResonanceConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_extra_kernel_splits_into_spin_and_neutral_parts(self) -> None:
        coordinates = self.value["action_normalized_coordinates"]
        self.assertIn("direct_sum", coordinates["decomposition"])
        self.assertEqual(coordinates["K_restricted_Gram"], [["9", "0"], ["0", "5116608"]])

    def test_common_zero_equations_are_necessary_and_sufficient(self) -> None:
        cone = self.value["common_zero_cone"]
        self.assertTrue(cone["necessary_and_sufficient"])
        self.assertIn("J_plus=0", cone["angular_equations"]["equivalence"])
        self.assertIn("A_minus", cone["energy_equation"])

    def test_nonaxisymmetric_witness(self) -> None:
        witness = self.value["nonaxisymmetric_witness"]
        self.assertEqual(witness["J_x_J_y_J_z"], ["0", "0", "0"])
        self.assertEqual(witness["A_minus"], "24+8*sqrt(3)")

    def test_regular_stratum_dimension(self) -> None:
        self.assertEqual(self.value["regularity_witness"]["rank"], 4)
        self.assertEqual(self.value["common_zero_cone"]["generic_smooth_stratum_real_dimension"], 28)

    def test_scope_is_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["bounded_full_second_order_equation_solved_on_common_cone"])
        self.assertFalse(classification["causal_retarded_sufficiency"])


if __name__ == "__main__":
    unittest.main()
