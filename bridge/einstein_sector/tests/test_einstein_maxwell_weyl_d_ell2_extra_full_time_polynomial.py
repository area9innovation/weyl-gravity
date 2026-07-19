"""Tests for the full-time d times ell2-extra polynomial repair."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_d_ell2_extra_full_time_polynomial import OUTPUT, build


class FullTimeDPolynomialTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_three_zero_columns_one_nonzero_column(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["axial_d_extra_t_coefficient_zero"])
        self.assertTrue(classification["polar_e1_d_extra_t_coefficient_zero"])
        self.assertTrue(classification["polar_e2_d_extra_t_coefficient_nonzero"])

    def test_old_constant_projection_is_scoped(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["old_d_constant_adjoint_isomorphism_retained"])
        self.assertFalse(classification["old_d_result_was_complete_bounded_column"])

    def test_fail_closed_joint_cone(self) -> None:
        self.assertEqual(self.value["full_time_polynomial"]["polynomial_zero_locus_for_d_times_polar_extra_alone"], "d*z2=0")
        self.assertFalse(self.value["classification"]["simultaneous_a_d_polynomial_zero_locus_solved"])
        self.assertFalse(self.value["classification"]["full_bounded_cone_solved"])


if __name__ == "__main__":
    unittest.main()
