"""Tests for the candidate-13 relative derived-source crosswalk."""

import json
import unittest

from bridge.einstein_sector.einstein_weyl_relative_candidate13_derived_source_crosswalk import OUTPUT, build


class RelativeCandidate13DerivedSourceCrosswalkTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build())

    def test_derived_source_does_not_promote_full_f2(self) -> None:
        payload = build()
        self.assertEqual(payload["morphism_disposition"]["derived_reduced_source_second_order_solve"], "CERTIFIED_SMOOTH_ONLY")
        self.assertEqual(payload["morphism_disposition"]["full_domain_support_local_f2"], "OBSTRUCTED")
        self.assertEqual(payload["morphism_disposition"]["full_relative_arity_two_morphism"], "OPEN")
        self.assertFalse(payload["morphism_disposition"]["arity_three_authorized"])

    def test_receivers_remain_typed(self) -> None:
        payload = build()
        self.assertEqual(len(payload["quadratic_receiver"]["zero_block_map"]["components"]), 5)
        self.assertIn("R_c=", payload["quadratic_receiver"]["bounded_pressure_map"]["components"])
        self.assertIn("18-dimensional", payload["quadratic_receiver"]["relative_resonance_map"]["target"])
        self.assertIn("distinct summands", payload["quadratic_receiver"]["typing"])


if __name__ == "__main__":
    unittest.main()
