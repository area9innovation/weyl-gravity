"""Tests for the global axial ell2 all-m bounded cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_global_axial_ell2_all_m_minus_extra_bounded_cone import OUTPUT, build


class GlobalAxialEll2AllMConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_all_m_promotion(self) -> None:
        self.assertEqual(self.value["SO3_shell_promotion"]["all_m"], [-2, -1, 0, 1, 2])

    def test_complete_union(self) -> None:
        self.assertTrue(self.value["complete_bounded_cone"]["union_is_necessary_and_sufficient"])

    def test_scope_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["polar_input_classified"])
        self.assertFalse(self.value["classification"]["general_ell_or_nonzero_momentum_classified"])


if __name__ == "__main__":
    unittest.main()
