"""Tests for the normalized BT additive Ward-frame certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_normalized_additive_ward_frame import (
    CERT_PATH,
    build,
    cycle_fixture,
)
from reverse_physics.verify_bt_euclidean_normalized_additive_ward_frame import (
    independent_cycle,
    verify,
)


class ExactFrameTests(unittest.TestCase):
    def test_producer_fixture(self) -> None:
        exact = cycle_fixture()
        self.assertEqual(exact["diversity"], Fraction(56, 81))
        self.assertEqual(exact["normalized_residual_energy"], 2)
        self.assertEqual(exact["action_pairing"], Fraction(47, 6))
        self.assertEqual(exact["diversity_flow"], Fraction(208, 6561))
        self.assertEqual(
            exact["phase_gram"],
            [[Fraction(4, 9), Fraction()], [Fraction(), Fraction(5, 9)]],
        )

    def test_independent_fixture(self) -> None:
        exact = independent_cycle()
        self.assertEqual(exact["diversity"], Fraction(56, 81))
        self.assertEqual(exact["energy"], 2)
        self.assertEqual(exact["source_pairing"], Fraction(-2, 9))
        self.assertEqual(exact["diversity_flow"], Fraction(208, 6561))
        self.assertEqual(exact["second_harmonic"], Fraction(-1, 9))


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

    def test_mutation_divergence_sign(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["normalized_additive_frame"].__setitem__(
                "restricted_divergence",
                "div_H X_a=+sum_x a_x*pi_x*(1-pi_x)",
            )
        )

    def test_mutation_residual_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["constant_frame_corollary"].__setitem__(
                "volume_uniform_bound",
                "E_mu[sum_x pi_x*r_x^2]<=lambda^2/N",
            )
        )

    def test_mutation_source_normalization(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["fourier_source_corollary"].__setitem__(
                "source_identity", "E_mu[F_b*Y_a]=sum_x a_x*b_x"
            )
        )

    def test_mutation_full_phase_eigenvalue(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["full_phase_stein_matrix"].__setitem__(
                "eigenvalues", "eigenvalues(G)=1+|z_2|,1-|z_2|"
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
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
