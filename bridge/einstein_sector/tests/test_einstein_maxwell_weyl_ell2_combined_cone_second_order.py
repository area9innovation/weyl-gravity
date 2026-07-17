"""Regression tests for the complete combined ell=2 cone."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_combined_cone_second_order import DEFAULT_OUTPUT, build_certificate


class Ell2CombinedConeSecondOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_complete_combined_cone(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["complete_combined_ell2_k0_common_zero_cone_second_order_extendible"])
        self.assertTrue(classification["cancellations_between_axial_and_polar_moment_maps_included"])

    def test_scope_boundary(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["general_ell_classified"])
        self.assertFalse(classification["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
