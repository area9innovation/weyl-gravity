"""Tests for the BT canonical phase-score connection certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_canonical_phase_score_connection import (
    CERT_PATH,
    build,
    phase_fixture,
)
from reverse_physics.verify_bt_euclidean_canonical_phase_score_connection import (
    independent_fixture,
    verify,
)


class ExactFixtureTests(unittest.TestCase):
    def test_producer_fixture(self) -> None:
        exact = phase_fixture()
        self.assertEqual(
            exact["gram"],
            [[Fraction(4, 9), Fraction()], [Fraction(), Fraction(5, 9)]],
        )
        self.assertEqual(
            exact["inverse_derivatives"][1],
            [
                [Fraction(5, 768), Fraction()],
                [Fraction(), Fraction(-1, 240)],
            ],
        )
        self.assertEqual(
            exact["connection_direct"], [Fraction(), Fraction(-1, 240)]
        )
        self.assertEqual(
            exact["connection_direct"], exact["connection_leverage"]
        )
        self.assertEqual(exact["lift_norm_sum"], Fraction(109, 6400))

    def test_independent_fixture(self) -> None:
        exact = independent_fixture()
        self.assertEqual(
            exact["connection_direct"], (Fraction(), Fraction(-1, 240))
        )
        self.assertEqual(
            exact["connection_direct"], exact["connection_leverage"]
        )
        self.assertEqual(exact["weight_sum"], Fraction(59, 12960))
        self.assertLessEqual(exact["lift_norm_sum"], exact["inverse_trace"])


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

    def test_mutation_connection_sign(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["connection_derivation"].__setitem__(
                "connection_formula",
                "C=-sum_x pi_x^2*(ell_x-1)*G^-1*h(x)",
            )
        )

    def test_mutation_connection_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["connection_control"].__setitem__(
                "pointwise_bound", "|C|<=1"
            )
        )

    def test_mutation_score_normalization(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["canonical_score"].__setitem__(
                "source_normalization", "E[F_k*S_i]=delta_ik/2"
            )
        )

    def test_mutation_residual_moment_recursion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["weighted_residual_moment_hierarchy"].__setitem__(
                "recursion",
                "E[R^(n+1)]<=lambda^2*(n+1)*E[R^n], n>=1",
            )
        )

    def test_mutation_coercivity_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "canonical_score_coercivity", "PROVED"
            )
        )

    def test_mutation_field_moment_promotion(self) -> None:
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

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("continuum_measure", "PROVED")
        )


if __name__ == "__main__":
    unittest.main()
