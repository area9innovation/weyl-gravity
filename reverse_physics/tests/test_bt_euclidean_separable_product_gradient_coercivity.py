"""Tests for the sharp separable-product BT gradient theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_separable_product_gradient_coercivity import (
    CERT_PATH,
    build,
    sine_fixture,
)
from reverse_physics.verify_bt_euclidean_separable_product_gradient_coercivity import (
    decode,
    independently_reconstruct_fixture,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_laurent_fourier_reconstruction(self) -> None:
        fixture = sine_fixture()
        rebuilt = independently_reconstruct_fixture()
        self.assertEqual(rebuilt["residual_norm"], decode(fixture["total_residual_norm_squared"]))
        self.assertEqual(rebuilt["euler_norm"], decode(fixture["total_euler_norm_squared"]))
        self.assertEqual(rebuilt["decomposition_difference_norm"], 0)

    def test_exact_fixture_values(self) -> None:
        rebuilt = independently_reconstruct_fixture()
        self.assertEqual(rebuilt["residual_norm"], Fraction(87, 8))
        self.assertEqual(rebuilt["euler_norm"], Fraction(973, 4))
        self.assertEqual(rebuilt["pair_norm"], Fraction(21))

    def test_sharp_gap(self) -> None:
        fixture = sine_fixture()
        self.assertEqual(decode(fixture["sharp_bound_slack"]), Fraction(1859, 8))


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
        mutate(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_fixture(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_fixture"]["total_euler_norm_squared"].__setitem__("numerator", 1)
        )

    def test_mutation_theorem(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["theorem"].__setitem__(
                "conclusion", "||E||_2^2>=0"
            )
        )

    def test_mutation_method_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "interacting_h_minus_one_bound", "PROVED"
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
