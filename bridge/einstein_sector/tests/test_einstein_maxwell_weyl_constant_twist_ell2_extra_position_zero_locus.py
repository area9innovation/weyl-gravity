"""Tests for the constant-twist ell2 extra position zero locus."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_constant_twist_ell2_extra_position_zero_locus import OUTPUT, build


class ConstantTwistEll2ExtraPositionZeroLocusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_rank_and_nullity(self) -> None:
        self.assertEqual(self.value["multiplicity_matrix"]["rank"], 2)
        self.assertEqual(self.value["complete_zero_locus"]["operator_rank"], 8)
        self.assertEqual(self.value["complete_zero_locus"]["kernel_positive_frequency_complex_dimension"], 12)

    def test_axisymmetric_face_survives(self) -> None:
        self.assertIn("m_A=0", self.value["fixtures"]["aligned_face"])

    def test_off_axis_kernel_is_nontrivial(self) -> None:
        self.assertTrue(self.value["classification"]["off_axis_kernel_strictly_nonzero"])
        self.assertIn("polar_e1", self.value["multiplicity_matrix"]["kernel_description"])

    def test_scope_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["Einstein_q_primary_twist_position_map_classified"])
        self.assertFalse(self.value["classification"]["full_second_order_equation_solved"])


if __name__ == "__main__":
    unittest.main()
