"""Tests for the BT annealed signed-response one-loop certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_annealed_response_one_loop import (
    CERT_PATH,
    build,
    exact_l6_coefficient,
    symbol_value,
)
from reverse_physics.verify_bt_euclidean_annealed_response_one_loop import (
    independent_l6,
    partition_symbol,
    verify,
)


class ExactCoefficientTests(unittest.TestCase):
    def test_independent_symbol_representation(self) -> None:
        values = (
            Fraction(2, 3),
            Fraction(5, 7),
            Fraction(11, 13),
            Fraction(17, 19),
        )
        self.assertEqual(symbol_value(values), partition_symbol(values))

    def test_exact_l6_sum(self) -> None:
        expected = Fraction(-849547889, 1849425177600)
        self.assertEqual(exact_l6_coefficient(), expected)
        self.assertEqual(independent_l6(), expected)
        self.assertLess(expected, 0)


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

    def test_mutation_l6_coefficient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_l6_decision"]["coefficient"].__setitem__(
                "numerator", 849547889
            )
        )

    def test_mutation_symbol(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["one_loop_symbol"].__setitem__("P", "0")
        )

    def test_mutation_large_volume_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["large_volume_reduction"].__setitem__(
                "sign_status", "PROVED_NEGATIVE"
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
