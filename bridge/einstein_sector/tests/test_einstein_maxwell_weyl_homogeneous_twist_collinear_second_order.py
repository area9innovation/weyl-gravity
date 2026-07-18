"""Tests for the collinear homogeneous/twist second-order theorem."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_twist_collinear_second_order import DEFAULT_OUTPUT


class HomogeneousTwistCollinearTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_certificate_identity(self) -> None:
        self.assertEqual(
            self.payload["result_id"],
            "EINSTEIN_MAXWELL_WEYL_HOMOGENEOUS_TWIST_COLLINEAR_SECOND_ORDER",
        )

    def test_complete_collinear_face(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["complete_collinear_standard_homogeneous_twist_common_zero_face_second_order_extendible"])
        self.assertTrue(classification["full_SO3_covariant_collinear_cone_classified"])

    def test_stronger_than_time_translation(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["time_translation_orbit_strictly_enlarged"])
        self.assertTrue(classification["arbitrary_c_and_d_included"])

    def test_open_boundary(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["physical_or_extra_ell1_inputs_classified"])
        self.assertFalse(classification["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
