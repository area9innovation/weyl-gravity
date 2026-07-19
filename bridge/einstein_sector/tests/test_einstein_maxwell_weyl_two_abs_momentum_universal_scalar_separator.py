"""Tests for the universal signed 1:-2 scalar separator."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_universal_scalar_separator import OUTPUT, build


class UniversalScalarSeparatorTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build())

    def test_all_candidates_are_covered(self) -> None:
        payload = build()
        self.assertEqual(len(payload["candidate_coverage"]), 15)
        self.assertTrue(all(row["bounded_generic_cone"] == "{0}" for row in payload["candidate_coverage"]))
        self.assertEqual(payload["uncovered_same_sign_candidates"]["candidate_indices"], [16, 17, 18, 19, 20, 21])

    def test_universal_factorizations_are_recorded(self) -> None:
        construction = build()["universal_construction"]
        self.assertIn("(omega-t1)", construction["n1_factorization"])
        self.assertIn("(omega-t2)", construction["nminus2_factorization"])

    def test_scope_is_fail_closed(self) -> None:
        flags = build()["classification"]
        self.assertFalse(flags["smooth_cones_classified_here"])
        self.assertFalse(flags["exceptional_or_generalized_zero_inputs_included"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
