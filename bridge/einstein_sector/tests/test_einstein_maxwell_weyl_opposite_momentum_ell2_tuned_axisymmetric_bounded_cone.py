"""Tests for the tuned axisymmetric bounded cone."""

from __future__ import annotations

import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_ell2_tuned_axisymmetric_bounded_cone import build


class TunedAxisymmetricBoundedConeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()

    def test_complete_resonance_decomposition(self) -> None:
        zero_set = self.payload["resonance_zero_set"]["complete_complex_zero_set"]
        self.assertEqual(len(zero_set), 4)
        self.assertIn("C_plus", zero_set[0])
        self.assertIn("T_minus_zero", zero_set[-1])

    def test_nonzero_common_zero_has_two_components(self) -> None:
        components = self.payload["nonzero_bounded_components"]
        self.assertEqual(components["signs"], ["sigma=+1", "sigma=-1"])
        self.assertTrue(components["complete_imbalance_interval"]["reciprocal_endpoints"])
        self.assertTrue(self.payload["classification"]["one_sided_travelling_components_excluded_by_momentum_balance"])

    def test_lifecycle_is_fail_closed(self) -> None:
        classes = self.payload["correction_classes"]
        self.assertEqual(classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "CERTIFIED")
        self.assertEqual(classes["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"], "CERTIFIED")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")
        self.assertFalse(self.payload["classification"]["p_primary_inputs_included"])
        self.assertFalse(self.payload["classification"]["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
