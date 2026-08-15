"""Tests for BT axial-slice quadratic coercivity."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_axial_slice_quadratic_coercivity import (
    CERT_PATH,
    build,
    fixture,
)
from reverse_physics.verify_bt_euclidean_axial_slice_quadratic_coercivity import (
    independent_fixture,
    verify,
)


class ExactFixtureTests(unittest.TestCase):
    def test_producer_fixture(self) -> None:
        exact = fixture()
        self.assertEqual(exact["action"], Fraction(1361, 2))
        self.assertEqual(exact["slice_cauchy_lower"], Fraction(2261, 8))
        self.assertEqual(
            exact["slice_laplacian_coefficients"],
            [Fraction(0), Fraction(-2), Fraction(0), Fraction(2)],
        )

    def test_independent_fixture(self) -> None:
        exact = independent_fixture()
        self.assertEqual(exact["action"], Fraction(1361, 2))
        self.assertEqual(exact["positive_norm"], Fraction(4))
        self.assertEqual(exact["fourier_lemma_rhs"], Fraction(8, 3))


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

    def test_mutation_action(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_nonseparable_l4_fixture"]["action"].__setitem__(
                "numerator", 1360
            )
        )

    def test_mutation_quadratic_constant(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["lowest_mode_corollary"].__setitem__(
                "log_field_bound",
                "A(psi)>=(N*omega_L^2/2)*|psi_hat(e_mu)|^2",
            )
        )

    def test_mutation_normalized_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "normalized_lowest_mode_second_moment", "PROVED"
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "PROVED"
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
