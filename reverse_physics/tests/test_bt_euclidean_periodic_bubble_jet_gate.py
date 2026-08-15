"""Tests for the BT periodic-bubble jet gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_periodic_bubble_jet_gate import (
    CERT_PATH,
    build,
    chord_angular_moment,
    sphere_even_moment,
    weak_field_fourth_stencil_quotient,
)
from reverse_physics.verify_bt_euclidean_periodic_bubble_jet_gate import (
    exact_polynomial_reconstruction,
    taylor_coefficient,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_independent_quartic_reconstruction(self) -> None:
        rebuilt = exact_polynomial_reconstruction()
        self.assertEqual(rebuilt["q4"], rebuilt["expected_q4"])
        self.assertEqual(rebuilt["laplacian_q4"], {})
        self.assertEqual(rebuilt["q4_square_average"], Fraction(1, 10))

    def test_sphere_moments(self) -> None:
        self.assertEqual(sphere_even_moment((2, 0, 0, 0)), Fraction(1, 8))
        self.assertEqual(sphere_even_moment((4, 0, 0, 0)), Fraction(7, 128))
        self.assertEqual(sphere_even_moment((2, 2, 0, 0)), Fraction(3, 640))
        self.assertEqual(chord_angular_moment(), Fraction(1, 10))

    def test_repaired_taylor_coefficients(self) -> None:
        harmonics = {1: Fraction(8, 3), 2: Fraction(-1, 6)}
        self.assertEqual(taylor_coefficient(harmonics, 2), 1)
        self.assertEqual(taylor_coefficient(harmonics, 4), 0)
        self.assertEqual(taylor_coefficient(harmonics, 6), Fraction(-1, 90))
        self.assertEqual(
            exact_polynomial_reconstruction()["q6"],
            exact_polynomial_reconstruction()["expected_q6"],
        )

    def test_weak_field_quotient(self) -> None:
        self.assertEqual(weak_field_fourth_stencil_quotient(), Fraction(32, 17))


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

    def test_mutation_log_coefficient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["naive_chord_obstruction"].__setitem__(
                "gradient_asymptotic", "unknown"
            )
        )

    def test_mutation_angular_moment(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["naive_chord_obstruction"]["sphere_moments"][
                "average_Q_4_squared"
            ].__setitem__("numerator", 2)
        )

    def test_mutation_repair_status(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["fourth_order_local_repair"].__setitem__(
                "status", "GLOBAL_REPAIR_PROVED"
            )
        )

    def test_mutation_weak_quotient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["weak_field_endpoint"]["value"].__setitem__(
                "numerator", 31
            )
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
