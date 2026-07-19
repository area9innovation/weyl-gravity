"""Tests for the polar ell2 Einstein-minus global resonance theorem."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_abd_polar_ell2_minus_resonance import OUTPUT, build


class PolarEll2MinusGlobalResonanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_rational_triangular_pivots(self) -> None:
        self.assertEqual(self.value["bounded_zero_locus"]["triangular_pivots"], {"b_t3": "66*b*z", "a_t2_after_b_zero": "198*a*z", "d_t_after_a_b_zero": "198*d*z"})

    def test_direct_linear_remainder_zero(self) -> None:
        self.assertEqual(self.value["linear_input"]["direct_action_row_remainder"], ["0", "0", "0", "0"])

    def test_nonzero_branch_zero_locus(self) -> None:
        self.assertEqual(self.value["bounded_zero_locus"]["nonzero_wave_branch"], "z!=0 implies a=b=d=0")

    def test_scope_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["all_m_promoted"])
        self.assertFalse(self.value["classification"]["complete_bounded_cone_solved"])


if __name__ == "__main__":
    unittest.main()
