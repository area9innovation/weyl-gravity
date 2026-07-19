from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L3_zero_variety import OUTPUT, build
from bridge.einstein_sector.verify_einstein_maxwell_weyl_ell2_two_abs_momentum_scalar_L3_zero_variety import verify


class ScalarL3ZeroVarietyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_certificate_is_current(self) -> None:
        self.assertEqual(build(), self.value)

    def test_independent_verifier(self) -> None:
        verify()

    def test_parity_pencil_is_exactly_diagonalized(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["parity_pencil_diagonalized_exactly"])
        self.assertTrue(classification["lambda_squared_positive_exactly"])

    def test_zero_variety_is_one_twelve_dimensional_product(self) -> None:
        zero = self.value["zero_variety"]
        self.assertEqual(zero["dimension_over_C"], 12)
        self.assertEqual(zero["irreducible_components_over_C"], 1)
        self.assertIn("all twenty 2-by-2 minors", zero["defining_minors"])

    def test_higher_lifecycles_are_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["same_fibre_quadratic_sources_classified"])
        self.assertFalse(classification["taub_common_zero_intersection_classified"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])
        self.assertFalse(classification["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
