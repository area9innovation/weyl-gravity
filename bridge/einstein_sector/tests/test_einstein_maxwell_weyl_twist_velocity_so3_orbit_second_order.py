"""Tests for the SO(3) twist-velocity corollary."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_twist_velocity_so3_orbit_second_order import DEFAULT_OUTPUT, build_certificate


class TwistVelocitySO3OrbitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8")), self.payload)

    def test_complete_A_zero_orbit(self) -> None:
        self.assertTrue(self.payload["classification"]["complete_A_zero_twist_velocity_SO3_orbit_second_order_extendible"])

    def test_new_A_gate_remains_open(self) -> None:
        self.assertFalse(self.payload["classification"]["nonzero_collinear_twist_position_classified"])


if __name__ == "__main__":
    unittest.main()
