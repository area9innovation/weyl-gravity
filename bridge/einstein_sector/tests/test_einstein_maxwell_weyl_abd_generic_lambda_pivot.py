"""Tests for the generic-lambda a,b,d pivot theorem."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_abd_generic_lambda_pivot import OUTPUT, build


class GenericLambdaPivotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_symbolic_not_interpolated(self) -> None:
        derivation = self.value["generic_lambda_derivation"]
        self.assertTrue(derivation["not_interpolation"])
        self.assertGreaterEqual(
            derivation["maximum_harmonic_jet_order"],
            derivation["Bach_Maxwell_maximum_sphere_derivative_order"] + 2,
        )
        remainders = derivation["Legendre_ODE_remainder_through_degree_6"]
        self.assertEqual(remainders, {"even": ["0"] * 7, "odd": ["0"] * 7})

    def test_local_jet_is_not_a_mode_identification(self) -> None:
        role = self.value["SO3_promotion"]["jet_normalization_role"]
        self.assertIn("local normalization", role)
        self.assertIn("not an identification", role)

    def test_all_ell_both_parities(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["all_fixed_ell_at_least_2_pivots_nonzero"])
        self.assertTrue(classification["both_parities_classified"])
        self.assertTrue(classification["all_m_promoted"])

    def test_scope_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["nonzero_momentum_classified"])
        self.assertFalse(classification["complete_global_wave_cone_classified"])


if __name__ == "__main__":
    unittest.main()
