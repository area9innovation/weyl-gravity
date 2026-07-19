"""Tests for the axial ell2 all-m bounded completion."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_all_m_bounded_completion import OUTPUT, build


class AxialEll2AllMBoundedCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_constant_l1_inverse(self) -> None:
        self.assertEqual(self.value["zero_frequency_L1_completion"]["remainder"], ["0"] * 4)
        self.assertTrue(self.value["zero_frequency_L1_completion"]["bounded"])

    def test_bounded_cone(self) -> None:
        self.assertTrue(self.value["second_order_theorem"]["bounded_or_finite_quasiperiodic"])

    def test_scope_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["polar_input_parity_classified"])
        self.assertFalse(self.value["classification"]["general_ell_classified"])


if __name__ == "__main__":
    unittest.main()
