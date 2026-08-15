"""Tests for the BT reciprocal-phase inverse-ellipticity certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_reciprocal_phase_inverse_ellipticity import (
    CERT_PATH,
    alternating_fixture,
    build,
)
from reverse_physics.verify_bt_euclidean_reciprocal_phase_inverse_ellipticity import (
    independent_fixture,
    verify,
)


class ExactFixtureTests(unittest.TestCase):
    def test_producer_fixture(self) -> None:
        exact = alternating_fixture()
        self.assertEqual(exact["weighted_residual_energy"], Fraction(18688, 81))
        self.assertEqual(exact["reciprocal_edge_sum"], Fraction(128, 9))
        self.assertEqual(exact["weighted_cauchy_product"], Fraction(64, 25))
        self.assertEqual(exact["pointwise_lower_bound"], Fraction(4096, 25))
        self.assertEqual(exact["lower_bound_ratio"], Fraction(1825, 1296))

    def test_independent_fixture(self) -> None:
        exact = independent_fixture()
        self.assertEqual(exact["energy"], Fraction(18688, 81))
        self.assertEqual(exact["harmonic_factor"], Fraction(9, 50))
        self.assertEqual(exact["telescoping"], Fraction(8, 5))
        self.assertGreaterEqual(exact["edge_sum"] ** 2, exact["lower"])
        self.assertEqual(exact["diversity"], Fraction(6359, 6400))


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

    def test_mutation_pointwise_constant(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["pointwise_localization_bound"].__setitem__(
                "theorem",
                "sum_x pi_x*r_x^2>=4*s_L^4*c^4/delta^2",
            )
        )

    def test_mutation_uncertainty_factor(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["weighted_phase_uncertainty"].__setitem__(
                "consequence", "Q(pi)>=2*s_L^2*c^2/delta"
            )
        )

    def test_mutation_inverse_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["inverse_phase_ellipticity"].__setitem__(
                "exact_bound",
                "E_mu[operator_norm(G^-1)^2]<=4",
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

    def test_mutation_dependency_tag(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("continuum_measure", "PROVED")
        )


if __name__ == "__main__":
    unittest.main()
