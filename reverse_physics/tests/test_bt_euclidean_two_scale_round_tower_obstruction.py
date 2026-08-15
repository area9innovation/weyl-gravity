"""Tests for the two-scale round BT tower obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_two_scale_round_tower_obstruction import (
    CERT_PATH,
    asymptotic_constants,
    build,
    closed_q_and_derivative,
    direct_q_and_derivative,
)
from reverse_physics.verify_bt_euclidean_two_scale_round_tower_obstruction import (
    reconstruct_algebra,
    verify,
)


class ExactAsymptoticTests(unittest.TestCase):
    def test_exact_radial_formula(self) -> None:
        fixture = (Fraction(2, 7), Fraction(1, 5))
        self.assertEqual(
            direct_q_and_derivative(*fixture),
            closed_q_and_derivative(*fixture),
        )

    def test_constants(self) -> None:
        producer = asymptotic_constants()
        verifier = reconstruct_algebra()
        self.assertEqual(verifier["euler_norm"], Fraction(9216, 5))
        self.assertEqual(verifier["residual"], Fraction(64, 3))
        self.assertEqual(verifier["quotient"], Fraction(432, 5))
        self.assertEqual(producer["quotient_coefficient"]["numerator"], 432)


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

    def test_mutation_euler_coefficient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["asymptotics"]["constants"][
                "euler_norm_coefficient_without_pi2"
            ].__setitem__("numerator", 9215)
        )

    def test_mutation_q_derivative(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_radial_algebra"].__setitem__(
                "q_derivative", "wrong"
            )
        )

    def test_mutation_periodic_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "periodized_two_scale_tower", "OBSTRUCTED"
            )
        )

    def test_mutation_witten_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "volume_uniform_witten_coercivity", "PROVED"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(2, "LORENTZIAN-CAUSAL")
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
