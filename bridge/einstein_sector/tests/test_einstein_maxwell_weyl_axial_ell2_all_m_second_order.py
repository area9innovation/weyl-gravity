"""Regression tests for the all-m axial ell=2 cone."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_all_m_second_order import DEFAULT_OUTPUT, build_certificate


class AxialEll2AllMSecondOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_all_m_closed(self) -> None:
        self.assertTrue(self.payload["classification"]["all_m_axial_ell2_common_zero_cone_second_order_extendible"])
        self.assertTrue(self.payload["classification"]["odd_L1_and_L3_channels_closed"])

    def test_scope_boundary(self) -> None:
        self.assertFalse(self.payload["classification"]["polar_input_parity_classified"])
        self.assertFalse(self.payload["classification"]["general_ell_classified"])


if __name__ == "__main__":
    unittest.main()
