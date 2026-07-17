"""Regression tests for the ell=2 neutral-face extension."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_neutral_face_second_order import DEFAULT_OUTPUT, build_certificate


class Ell2NeutralFaceSecondOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_is_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_strict_extension(self) -> None:
        self.assertTrue(self.payload["classification"]["paper91_boundary_ray_strictly_extended"])
        self.assertTrue(self.payload["classification"]["two_parameter_positive_quadrant_face_second_order_extendible"])

    def test_nine_channels(self) -> None:
        self.assertEqual(len(self.payload["nonzero_frequency_channel_ledger"]), 9)


if __name__ == "__main__":
    unittest.main()
