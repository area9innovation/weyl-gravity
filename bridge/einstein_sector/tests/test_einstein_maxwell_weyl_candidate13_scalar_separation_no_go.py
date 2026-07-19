"""Tests for the candidate-13 scalar-separation no-go."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_candidate13_scalar_separation_no_go import OUTPUT, build


class Candidate13ScalarSeparationTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build())

    def test_exact_lower_bounds_are_positive(self) -> None:
        lower = build()["exact_separation_certificate"]["strict_lower_bounds"]
        self.assertEqual(lower, {"qminus_n1": "379/1000", "p_n1": "101/250", "qminus_nminus2": "23/80", "p_nminus2": "38/45"})

    def test_bounded_cone_is_origin_but_smooth_is_not_collapsed(self) -> None:
        flags = build()["classification"]
        self.assertTrue(flags["candidate13_complete_bounded_cone_is_origin"])
        self.assertFalse(flags["candidate13_nonzero_bounded_point_exists"])
        self.assertFalse(flags["smooth_cone_collapses_to_origin"])

    def test_scope_remains_fail_closed(self) -> None:
        flags = build()["classification"]
        self.assertFalse(flags["exceptional_or_generalized_zero_inputs_included"])
        self.assertFalse(flags["all_orders_integrability"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
