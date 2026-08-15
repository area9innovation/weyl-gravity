"""Tests for the BT conformal-curvature bubble gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_conformal_curvature_bubble_gate import (
    CERT_PATH,
    beta_tail,
    build,
    floor_fixture,
)
from reverse_physics.verify_bt_euclidean_conformal_curvature_bubble_gate import (
    beta_tail_independent,
    reconstruct_floor_point,
    reconstruct_round_bubble,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_round_bubble_radial_identity(self) -> None:
        row = reconstruct_round_bubble(Fraction(7, 3), Fraction(11, 4))
        self.assertEqual(row["delta"], row["minus_two_omega_cubed"])
        self.assertEqual(row["residual"], row["minus_two_omega_squared"])
        self.assertEqual(row["scalar"], 12)

    def test_floor_fixture_independent_reconstruction(self) -> None:
        fixture = floor_fixture()
        row = reconstruct_floor_point(Fraction(2), Fraction(1, 3), Fraction(3))
        self.assertEqual(row["residual"], Fraction(-2, 27))
        self.assertEqual(row["q"], Fraction(-8, 27))
        self.assertEqual(row["euler_gradient"], Fraction(-8, 729))
        self.assertEqual(fixture["euler_gradient_E"]["numerator"], -8)

    def test_independent_beta_integrals(self) -> None:
        self.assertEqual(beta_tail(4), beta_tail_independent(4))
        self.assertEqual(beta_tail(6), beta_tail_independent(6))
        self.assertEqual(beta_tail(4), Fraction(1, 6))
        self.assertEqual(beta_tail(6), Fraction(1, 20))


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

    def test_mutation_floor_gradient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["positive_floor_bubble"]["exact_point_fixture"][
                "euler_gradient_E"
            ].__setitem__("numerator", -7)
        )

    def test_mutation_round_action(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["round_four_sphere_bubble"].__setitem__(
                "action", "unknown"
            )
        )

    def test_mutation_periodic_gate(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["torus_scaling_gate"].__setitem__("status", "PROVED")
        )

    def test_mutation_method_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "volume_uniform_witten_coercivity", "PROVED"
            )
        )

    def test_mutation_dependency_tag(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(
                2, "LORENTZIAN-CAUSAL"
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
