"""Tests for the complete coefficientwise candidate-13 mixed cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_complete_mixed_cone import OUTPUT, build


class Candidate13CompleteMixedConeTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build())

    def test_correction_classes_are_separate(self) -> None:
        payload = build()
        bounded = payload["tangent_cones"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]
        smooth = payload["tangent_cones"]["SMOOTH_EXPONENTIAL_POLYNOMIAL"]
        causal = payload["tangent_cones"]["CAUSAL_RETARDED"]
        self.assertEqual(bounded["status"], "CERTIFIED")
        self.assertIn("R_c=0", bounded["formula"])
        self.assertIn("R_13,18=0", bounded["formula"])
        self.assertNotIn("R_13", smooth["formula"])
        self.assertEqual(causal["status"], "NO_CERTIFIED_MAP")

    def test_geometry_remains_fail_closed(self) -> None:
        payload = build()
        self.assertFalse(payload["classification"]["nonzero_mixed_bounded_point_certified"])
        self.assertTrue(payload["classification"]["nonzero_mixed_smooth_point_certified"])
        self.assertTrue(payload["classification"]["complete_candidate13_bounded_tangent_cone_formula_certified"])
        self.assertFalse(payload["classification"]["real_algebraic_component_decomposition_classified"])
        self.assertFalse(payload["classification"]["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
