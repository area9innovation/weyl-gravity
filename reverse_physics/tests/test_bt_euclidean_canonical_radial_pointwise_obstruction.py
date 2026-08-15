"""Tests for the BT canonical-radial pointwise obstruction certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_canonical_radial_pointwise_obstruction import (
    CERT_PATH,
    additive_fixture,
    build,
    canonical_fixture,
)
from reverse_physics.verify_bt_euclidean_canonical_radial_pointwise_obstruction import (
    independent_additive,
    independent_canonical,
    verify,
)


class ExactFixtureTests(unittest.TestCase):
    def test_additive_fixture(self) -> None:
        produced = additive_fixture()
        independent = independent_additive()
        self.assertEqual(produced["field_dot_derivative_over_log2"], Fraction(540, 17))
        self.assertEqual(produced["field_dot_derivative_over_log2"], independent["dot"])
        self.assertGreater(independent["dot"], 0)

    def test_canonical_fixture(self) -> None:
        produced = canonical_fixture()
        independent = independent_canonical()
        self.assertEqual(produced["canonical_score"], [Fraction(), Fraction(563, 192)])
        self.assertEqual(produced["field_dot_score_over_log2"], Fraction(-563, 3))
        self.assertEqual(produced["field_dot_score_over_log2"], independent["dot"])
        self.assertLess(independent["dot"], 0)


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

    def test_mutation_additive_sign(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["additive_contraction_fixture"].__setitem__(
                "sign", "F dot (X_1 F)<0"
            )
        )

    def test_mutation_canonical_score(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["canonical_score_fixture"].__setitem__(
                "canonical_score",
                [{"numerator": 0, "denominator": 1}, {"numerator": -563, "denominator": 192}],
            )
        )

    def test_mutation_marginal_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "conditional_marginal_score_coercivity", "OBSTRUCTED"
            )
        )

    def test_mutation_witten_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "full_witten_form_coercivity", "OBSTRUCTED"
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "DIVERGES"
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("continuum_measure", "OBSTRUCTED")
        )


if __name__ == "__main__":
    unittest.main()
