"""Tests for the exact BT residual spectrahedral pushforward."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_residual_spectrahedral_pushforward import (
    CERT_PATH,
    build,
    cycle_fixture,
)
from reverse_physics.verify_bt_euclidean_residual_spectrahedral_pushforward import (
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def test_cycle_ground_state_and_tree_data(self) -> None:
        fixture = cycle_fixture()
        self.assertEqual(
            fixture["residual"],
            [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)],
        )
        self.assertEqual(
            fixture["cofactor_values"],
            [Fraction(5), Fraction(20), Fraction(5), Fraction(5, 4)],
        )
        self.assertEqual(fixture["tree_density"], 5)

    def test_cycle_coarea_jacobian(self) -> None:
        fixture = cycle_fixture()
        self.assertEqual(fixture["domain_gram_determinant"], 4)
        self.assertEqual(fixture["image_gram_determinant"], 7225)
        self.assertEqual(fixture["jacobian_squared"], Fraction(7225, 4))

    def test_deterministic_builder(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            committed = json.load(handle)
        self.assertEqual(build(), committed)


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.payload = json.load(handle)

    def verify_mutation(self, mutate) -> None:
        changed = copy.deepcopy(self.payload)
        mutate(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_independent_verifier(self) -> None:
        self.assertTrue(verify(CERT_PATH))

    def test_mutation_tree_cofactor(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_cycle_fixture"]["tree_cofactors"][1].__setitem__(
                "numerator", 19
            )
        )

    def test_mutation_jacobian(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_cycle_fixture"].__setitem__(
                "restricted_jacobian", {"numerator": 84, "denominator": 2}
            )
        )

    def test_mutation_marginal_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "normalized_lowest_mode_marginal_bound", "PROVED"
            )
        )

    def test_mutation_foundational_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["foundational_dependency_cut"].__setitem__(
                "weakest_base_or_reversal", "PROVED"
            )
        )

    def test_mutation_provenance(self) -> None:
        self.verify_mutation(
            lambda data: data["provenance"]["inputs"][0].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.verify_mutation(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
