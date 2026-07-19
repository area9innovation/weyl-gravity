"""Tests for the aligned global plus axial ell2 bounded cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_aligned_global_axial_ell2_minus_extra_bounded_cone import OUTPUT, build


class AlignedGlobalAxialEll2BoundedConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_two_branches(self) -> None:
        cone = self.value["complete_bounded_cone"]
        self.assertIn("wave=0", cone["static_branch"])
        self.assertIn("x_minus=", cone["wave_branch"])

    def test_electric_is_independently_removed(self) -> None:
        witness = self.value["necessity"]["zero_frequency"]["electric_independence_witness"]
        self.assertIn("Q_e=0", witness)

    def test_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["polar_or_all_m_input_classified"])
        self.assertFalse(classification["general_ell_or_nonzero_momentum_classified"])


if __name__ == "__main__":
    unittest.main()
