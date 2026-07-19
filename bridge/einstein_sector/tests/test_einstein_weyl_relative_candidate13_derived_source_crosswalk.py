"""Tests for the candidate-13 relative derived-source crosswalk."""

import json
import unittest

from bridge.einstein_sector.einstein_weyl_relative_candidate13_derived_source_crosswalk import OUTPUT, build


class RelativeCandidate13DerivedSourceCrosswalkTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build())

    def test_derived_source_does_not_promote_full_f2(self) -> None:
        payload = build()
        self.assertEqual(payload["morphism_disposition"]["derived_reduced_source_second_order_solve"], "CERTIFIED_BOUNDED_AND_SMOOTH_ON_THEIR_DECLARED_ZERO_LOCI")
        self.assertEqual(payload["morphism_disposition"]["full_domain_support_local_f2"], "OBSTRUCTED")
        self.assertEqual(payload["morphism_disposition"]["full_relative_arity_two_morphism"], "OPEN")
        self.assertFalse(payload["morphism_disposition"]["arity_three_authorized"])

    def test_receivers_remain_typed(self) -> None:
        payload = build()
        self.assertEqual(len(payload["quadratic_receiver"]["zero_block_map"]["components"]), 5)
        self.assertIn("R_c=", payload["quadratic_receiver"]["bounded_pressure_map"]["components"])
        self.assertIn("18-dimensional", payload["quadratic_receiver"]["relative_resonance_map"]["target"])
        self.assertIn("distinct summands", payload["quadratic_receiver"]["typing"])

    def test_bounded_pullback_is_certified_origin_but_smooth_is_nonempty(self) -> None:
        payload = build()
        flags = payload["classification"]
        self.assertTrue(flags["bounded_derived_source_pullback_is_origin"])
        self.assertFalse(flags["nonzero_mixed_bounded_derived_source_point_exists"])
        self.assertTrue(flags["nonzero_mixed_bounded_derived_source_point_nonexistence_certified"])
        self.assertTrue(flags["nonzero_mixed_smooth_derived_source_point_certified"])
        self.assertIn("={0}", payload["derived_source_pullback"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["domain"])


if __name__ == "__main__":
    unittest.main()
