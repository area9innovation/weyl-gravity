"""Regression tests for the axial ell=2 full-extra face."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_extra_face_second_order import DEFAULT_OUTPUT, build_certificate


class AxialEll2FullExtraFaceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_full_extra_face_extends(self) -> None:
        self.assertTrue(self.payload["classification"]["both_axial_extra_polarizations_included"])
        self.assertTrue(self.payload["classification"]["three_parameter_positive_cone_second_order_extendible"])

    def test_fail_closed(self) -> None:
        self.assertFalse(self.payload["classification"]["all_m_promoted"])
        self.assertFalse(self.payload["classification"]["opposite_momentum_phase_source_classified"])


if __name__ == "__main__":
    unittest.main()
