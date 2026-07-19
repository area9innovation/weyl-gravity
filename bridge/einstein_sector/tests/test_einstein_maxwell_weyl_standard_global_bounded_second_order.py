"""Tests for the standard generalized-zero bounded cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_standard_global_bounded_second_order import OUTPUT, build


class StandardGlobalBoundedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_polynomial_zero_locus(self) -> None:
        self.assertEqual(self.value["polynomial_growth_ideal"]["real_polynomial_zero_locus"], "b=0, B=0, Q_e*a=0")

    def test_bounded_cone_and_universal_elimination(self) -> None:
        self.assertEqual(
            self.value["moment_map_intersection"]["complete_bounded_tangent_cone"],
            "Z2_global^bounded={(c,d,W_x,A): c,d,W_x real, A in R^3}",
        )
        self.assertTrue(self.value["classification"]["universal_b_twist_velocity_and_Qe_a_elimination_on_complete_finite_carrier"])
        self.assertIn("Q_e*a=0", self.value["universal_complete_carrier_corollary"]["statement"])

    def test_fail_closed_remaining_scopes(self) -> None:
        self.assertFalse(self.value["classification"]["complete_finite_bounded_common_zero_locus_solved"])
        self.assertEqual(self.value["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
