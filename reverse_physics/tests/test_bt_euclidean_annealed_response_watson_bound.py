"""Tests for the BT annealed-response Watson bound."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_annealed_response_watson_bound import (
    CERT_PATH,
    build,
    diagonal_endpoint_count,
    origin_counts,
)
from reverse_physics.verify_bt_euclidean_annealed_response_watson_bound import (
    direct_diagonal_endpoint_count,
    multinomial_origin_counts,
    verify,
)


class ExactWalkTests(unittest.TestCase):
    def test_independent_origin_counts(self) -> None:
        producer, divisions = origin_counts(20)
        verifier = list(multinomial_origin_counts(20))
        self.assertEqual(producer, verifier)
        self.assertEqual(divisions, 19)

    def test_independent_endpoint_counts(self) -> None:
        self.assertEqual(
            [diagonal_endpoint_count(n) for n in range(11)],
            [direct_diagonal_endpoint_count(n) for n in range(11)],
        )

    def test_rational_threshold(self) -> None:
        bound = (
            -Fraction(85, 5184)
            + Fraction(31, 200) / 18
            + Fraction(5, 288) * Fraction(54, 125)
        )
        self.assertEqual(bound, Fraction(-37, 129600))
        self.assertLess(bound, 0)


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

    def test_mutation_watson_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["watson_return_series"]["certified_upper"].__setitem__(
                "numerator", 32
            )
        )

    def test_mutation_i_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["derivative_moment_potential_kernel"][
                "certified_upper"
            ].__setitem__("numerator", 55)
        )

    def test_mutation_limit_sign(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["large_volume_decision"].__setitem__(
                "sign", "NONNEGATIVE"
            )
        )

    def test_mutation_nonperturbative_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "nonperturbative_annealed_response", "PROVED_NEGATIVE"
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
