"""Tests for the complete candidate-13 bounded zero-frequency receiver."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_candidate13_bounded_zero_frequency_decomposition import OUTPUT, build


class Candidate13BoundedZeroFrequencyTests(unittest.TestCase):
    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), build())

    def test_six_functionals_are_complete(self) -> None:
        payload = build()
        self.assertEqual(payload["bounded_zero_frequency_decomposition"]["complete_functional_basis"], ["mu_H", "mu_Px", "mu_J1", "mu_J2", "mu_J3", "R_c"])
        self.assertTrue(payload["classification"]["five_stabilizers_plus_circle_pressure_necessary_and_sufficient"])

    def test_scope_is_fail_closed(self) -> None:
        flags = build()["classification"]
        self.assertFalse(flags["nonzero_frequency_candidate13_functionals_classified_here"])
        self.assertFalse(flags["all_orders_integrability"])
        self.assertFalse(flags["causal_residual_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
