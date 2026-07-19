"""Tests for the candidate-13 mixed bounded-extension join."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_candidate13_mixed_bounded_extension import OUTPUT, build


class Candidate13MixedBoundedExtensionTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build())

    def test_scope_stays_fail_closed(self) -> None:
        payload = build()
        self.assertEqual(payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OBSTRUCTED")
        self.assertEqual(payload["correction_classes"]["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"], "CERTIFIED")
        self.assertEqual(payload["correction_classes"]["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")
        self.assertFalse(payload["classification"]["full_candidate_13_mixed_tangent_cone_classified"])
        self.assertFalse(payload["classification"]["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
