"""Tests for the BT unique-critical-point and gradient gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_unique_critical_point_gradient_gate import (
    CERT_PATH,
    build,
    exact_fixture,
)
from reverse_physics.verify_bt_euclidean_unique_critical_point_gradient_gate import (
    decode,
    independently_reconstruct_four_dimensional_embedding,
    independently_reconstruct_fixture,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_oriented_edge_reconstruction_agrees(self) -> None:
        fixture = exact_fixture()
        rebuilt = independently_reconstruct_fixture(
            fixture["omega_integer_pattern"]
        )
        self.assertEqual(
            rebuilt["residual_norm"], decode(fixture["residual_norm_squared"])
        )
        self.assertEqual(
            rebuilt["gradient_norm"], decode(fixture["gradient_norm_squared"])
        )
        self.assertEqual(rebuilt["quotient"], decode(fixture["gradient_quotient"]))

    def test_exact_free_sharp_gap(self) -> None:
        fixture = exact_fixture()
        quotient = decode(fixture["gradient_quotient"])
        gap = decode(fixture["strict_gap_below_free_sharp_target"])
        self.assertLess(quotient, Fraction(4))
        self.assertGreater(gap, 0)

    def test_graph_conservation_identities(self) -> None:
        rebuilt = independently_reconstruct_fixture(
            exact_fixture()["omega_integer_pattern"]
        )
        self.assertEqual(rebuilt["gradient_sum"], 0)
        self.assertEqual(rebuilt["laplacian_sum"], 0)
        self.assertEqual(rebuilt["weighted_residual_sum"], 0)

    def test_four_dimensional_embedding_is_enumerated(self) -> None:
        fixture = exact_fixture()
        base = independently_reconstruct_fixture(fixture["omega_integer_pattern"])
        embedded = independently_reconstruct_four_dimensional_embedding(
            fixture["omega_integer_pattern"]
        )
        self.assertEqual(embedded["residual_norm"], 16 * base["residual_norm"])
        self.assertEqual(embedded["gradient_norm"], 16 * base["gradient_norm"])


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
            lambda cert: cert["exact_sharp_gradient_obstruction"][
                "omega_integer_pattern"
            ][0].__setitem__(0, 2020)
        )

    def test_mutation_quotient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_sharp_gradient_obstruction"][
                "gradient_quotient"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_critical_chain(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["unique_critical_point_theorem"].__setitem__(
                "left_kernel", "unknown"
            )
        )

    def test_mutation_method_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "weaker_global_gradient_domination", "PROVED"
            )
        )

    def test_mutation_dependency_tag(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(
                1, "LORENTZIAN-CAUSAL"
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
