"""Tests for the smooth-global paired opposite-momentum theorem."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_smooth_global_second_order import DEFAULT_OUTPUT, build_certificate


class OppositeMomentumSmoothGlobalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8")), self.payload)

    def test_complete_fixed_block_cone(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["opposite_momentum_relative_phases_classified_in_smooth_global_class"])
        self.assertTrue(classification["complete_fixed_ell_absolute_k_common_zero_cone_second_order_extendible"])

    def test_correction_class_is_explicit(self) -> None:
        correction = self.payload["correction_space"]
        self.assertIn("exponential-polynomial", correction["temporal"])
        self.assertFalse(correction["bounded_or_finite_quasiperiodic_required"])

    def test_boundaries_remain_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["bounded_or_finite_quasiperiodic_cone_classified"])
        self.assertFalse(classification["distinct_absolute_momentum_fibers_classified"])
        self.assertFalse(classification["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
