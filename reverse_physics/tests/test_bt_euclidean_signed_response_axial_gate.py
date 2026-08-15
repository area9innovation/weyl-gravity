"""Tests for the BT signed conditional-response axial gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_signed_response_axial_gate import (
    CERT_PATH,
    build,
    fiber_coefficient,
    vacuum_covariance_expansion,
)
from reverse_physics.verify_bt_euclidean_signed_response_axial_gate import (
    independent_expansion,
    verify,
)


class ExactExpansionTests(unittest.TestCase):
    def test_fiber_coefficients(self) -> None:
        self.assertEqual(
            [fiber_coefficient(degree) for degree in range(2, 7)],
            [Fraction(36), Fraction(-28), Fraction(21), Fraction(-7), Fraction(31, 10)],
        )

    def test_independent_expansion(self) -> None:
        producer = vacuum_covariance_expansion()
        verifier = independent_expansion()
        self.assertEqual(producer, verifier)
        self.assertEqual(producer["covariance"][2], Fraction(1, 72))
        self.assertEqual(producer["covariance"][4], Fraction(43, 46656))


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

    def test_mutation_covariance(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_weak_coupling_expansion"][
                "covariance_coefficients_lambda0_to_lambda4"
            ][4].__setitem__("numerator", 42)
        )

    def test_mutation_beta(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_weak_coupling_expansion"][
                "beta_lambda2_coefficient"
            ].__setitem__("numerator", 43)
        )

    def test_mutation_annealed_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "annealed_beta_nonnegative_or_lower_bound", "PROVED"
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
