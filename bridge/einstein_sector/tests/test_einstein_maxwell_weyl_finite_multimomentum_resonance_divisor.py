from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class FiniteMultimomentumDivisorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_finite_multimomentum_resonance_divisor.json").read_text())

    def test_divisor_is_linear_in_rho(self) -> None:
        divisor = self.value["exact_divisor"]
        self.assertIn("rho", divisor["linear_squared_divisor"])
        self.assertTrue(self.value["classification"]["squared_divisor_linear_in_circumference_parameter"])

    def test_squaring_sign_condition_is_retained(self) -> None:
        self.assertIn("tau*", self.value["exact_divisor"]["admissibility"])

    def test_one_fibre_formulas_are_recovered(self) -> None:
        reductions = self.value["certified_reductions"]
        self.assertTrue(reductions["opposite_equal_absolute_momentum"]["matches_existing_h0_divisor"])
        self.assertTrue(reductions["aligned_equal_absolute_momentum"]["matches_existing_h4_divisor"])

    def test_identity_channels_fail_closed(self) -> None:
        self.assertTrue(self.value["classification"]["identity_resonant_channels_fail_closed"])
        self.assertIn("explicit source-matrix row", self.value["exact_divisor"]["degenerate_cases"]["Q_zero_constant_zero"])

    def test_no_source_or_tangent_cone_is_inferred(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["quadratic_source_coefficients_computed"])
        self.assertFalse(classification["complete_multifibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
