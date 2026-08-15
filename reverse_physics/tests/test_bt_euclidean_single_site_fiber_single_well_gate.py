"""Tests for the BT one-site fiber single-well gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_single_site_fiber_single_well_gate import (
    CERT_PATH,
    build,
    fiber_coefficients,
    lattice_fixture,
    polynomial,
    polynomial_derivative,
    stationary_value_reduction,
)
from reverse_physics.verify_bt_euclidean_single_site_fiber_single_well_gate import (
    reconstruct_fixture,
    verify,
)


class ExactAlgebraTests(unittest.TestCase):
    def test_stationary_elimination(self) -> None:
        q_value = 8
        x = Fraction(7, 5)
        a_value = Fraction(11, 3)
        c2 = Fraction(13, 2)
        c1 = -(4 * c2 * x**3 + q_value * a_value) / (3 * x**2)
        self.assertEqual(
            polynomial(x, q_value, a_value, c2, c1),
            stationary_value_reduction(x, q_value, a_value, c2),
        )
        self.assertEqual(
            polynomial_derivative(x, q_value, a_value, c2, c1), 0
        )

    def test_fixture_reconstructed_from_lattice(self) -> None:
        fixture = lattice_fixture()
        rebuilt = reconstruct_fixture()
        self.assertEqual(rebuilt["A"], Fraction(4))
        self.assertEqual(rebuilt["C1"], Fraction(-121))
        self.assertEqual(rebuilt["curvature"], Fraction(-57))
        self.assertEqual(
            rebuilt["P3"],
            Fraction(fixture["P_at_3"]["numerator"], fixture["P_at_3"]["denominator"]),
        )

    def test_bad_edge_count_rejected(self) -> None:
        with self.assertRaises(ValueError):
            fiber_coefficients(8, [Fraction(1)] * 7, [Fraction(-1)] * 8)


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

    def test_mutation_curvature(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["nonconvex_fixture"]["fiber_curvature_at_z_0"].__setitem__(
                "numerator", -56
            )
        )

    def test_mutation_degree_margin(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["single_well_theorem"]["exact_q_less_than_16_margin"].__setitem__(
                "numerator", 0
            )
        )

    def test_mutation_local_gap_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "uniform_one_site_poincare", "PROVED"
            )
        )

    def test_mutation_global_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "interacting_h_minus_one_bound", "PROVED"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
