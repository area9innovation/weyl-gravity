"""Tests for the BT bosonic ground-state lift certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_bosonic_ground_state_lift import (
    CERT_PATH,
    build,
    fixture,
)
from reverse_physics.verify_bt_euclidean_bosonic_ground_state_lift import (
    independent_fixture,
    verify,
)


class ExactTheoremTests(unittest.TestCase):
    def test_rootwise_gaussian_identity(self) -> None:
        produced = fixture()
        independent = independent_fixture()
        self.assertEqual(tuple(produced["cofactors"]), independent["cofactors"])
        self.assertEqual(
            tuple(produced["integrated_factors"]),
            (Fraction(4, 125),) * 4,
        )

    def test_ground_state_conductance_tree_sum(self) -> None:
        independent = independent_fixture()
        self.assertEqual(
            independent["conductances"],
            (Fraction(2), Fraction(2), Fraction(1, 2), Fraction(1, 2)),
        )
        self.assertEqual(independent["tree_sum"], 5)


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

    def test_mutation_cofactor(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["cycle_four_fixture"]["principal_minors"][1].__setitem__(
                "numerator", 19
            )
        )

    def test_mutation_field_statistics(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["bosonic_lift_theorem"].__setitem__(
                "field_count", "two real anticommuting fields"
            )
        )

    def test_mutation_determinant_exponent(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["hyperbolic_comparator"].__setitem__(
                "vrjp_determinant_power", "-1 on the spanning-tree determinant"
            )
        )

    def test_mutation_direct_import_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "published_vrjp_hyperbolic_localization_direct_import", "PROVED"
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "BOUNDED"
            )
        )

    def test_mutation_extra_claim(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("continuum_identification", "PROVED")
        )


if __name__ == "__main__":
    unittest.main()
