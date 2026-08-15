"""Tests for the BT one-site uniform Poincare theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_single_site_uniform_poincare import (
    CERT_PATH,
    build,
    positivity_polynomials,
    radial_fixture,
)
from reverse_physics.verify_bt_euclidean_single_site_uniform_poincare import (
    left_closed_numerator,
    right_closed_numerator,
    verify,
)


class ExactAlgebraTests(unittest.TestCase):
    def test_polynomial_evaluations(self) -> None:
        polynomials = positivity_polynomials()
        for value in (Fraction(1), Fraction(3, 2), Fraction(4)):
            right = sum(
                coefficient * value**power
                for power, coefficient in enumerate(polynomials["right_power"])
            )
            left = sum(
                coefficient * value**power
                for power, coefficient in enumerate(polynomials["left_power"])
            )
            self.assertEqual(right, right_closed_numerator(value))
            self.assertEqual(left, left_closed_numerator(value))

    def test_shifted_coefficients_positive(self) -> None:
        polynomials = positivity_polynomials()
        self.assertTrue(all(value > 0 for value in polynomials["right_shifted"]))
        self.assertTrue(all(value > 0 for value in polynomials["left_shifted"]))

    def test_radial_fixture_signs(self) -> None:
        right, margin = radial_fixture(Fraction(4), Fraction(32), Fraction(2))
        left, left_margin = radial_fixture(
            Fraction(4), Fraction(32), Fraction(1, 2)
        )
        self.assertEqual(margin, 0)
        self.assertEqual(left_margin, 0)
        self.assertGreater(right, 0)
        self.assertLess(left, 0)


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.certificate = json.load(handle)

    def test_deterministic_builder(self) -> None:
        self.assertEqual(build(), self.certificate)

    def test_independent_verifier(self) -> None:
        self.assertTrue(verify(CERT_PATH))

    def assert_mutation_rejected(self, mutate) -> None:
        changed = copy.deepcopy(self.certificate)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            mutate(changed)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_polynomial(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_scalar_inequalities"][
                "left_square_polynomial_power_coefficients"
            ].__setitem__(6, 0)
        )

    def test_mutation_poincare_constant(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["hardy_muckenhoupt_transfer"].__setitem__(
                "phi_coordinate_poincare", "C_P,phi<=1 because psi=lambda*phi"
            )
        )

    def test_mutation_global_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "volume_uniform_global_poincare", "PROVED"
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "interacting_h_minus_one_bound", "PROVED"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
