"""Tests for the balanced homogeneous/twist second-order fixture."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_balanced_second_order import DEFAULT_OUTPUT, build_certificate


class HomogeneousTwistBalancedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8")), self.payload)

    def test_balance_normalization(self) -> None:
        self.assertEqual(self.payload["first_order_balance"]["common_zero_equation"], "3*a^2-4*B^2=0")

    def test_complete_declared_correction(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["all_polar_L2_tensor_rows_solved"])
        self.assertTrue(classification["all_axial_L1_rows_solved"])
        self.assertTrue(classification["nonzero_homogeneous_twist_velocity_common_zero_tangent_second_order_extendible"])

    def test_full_cone_remains_open(self) -> None:
        self.assertFalse(self.payload["classification"]["full_twist_velocity_cone_classified"])


if __name__ == "__main__":
    unittest.main()
