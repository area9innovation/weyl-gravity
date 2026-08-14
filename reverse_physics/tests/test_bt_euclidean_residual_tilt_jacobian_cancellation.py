"""Tests for the exact BT residual-tilt Jacobian cancellation."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_residual_tilt_jacobian_cancellation import (
    CERT_PATH,
    build,
    cycle_data,
)
from reverse_physics.verify_bt_euclidean_residual_tilt_jacobian_cancellation import (
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def test_base_cycle_fixture(self) -> None:
        fixture = cycle_data(
            [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
        )
        self.assertEqual(
            fixture["residual"],
            [Fraction(1, 2), Fraction(-1), Fraction(1, 2), Fraction(2)],
        )
        self.assertEqual(fixture["action"], Fraction(11, 4))
        self.assertEqual(fixture["tree_density"], Fraction(5))
        self.assertEqual(fixture["coarea_jacobian"], Fraction(85, 2))

    def test_shifted_cycle_fixture(self) -> None:
        fixture = cycle_data(
            [Fraction(2), Fraction(1), Fraction(1), Fraction(1, 2)]
        )
        self.assertEqual(
            fixture["residual"],
            [Fraction(-5, 4), Fraction(1), Fraction(-1, 2), Fraction(4)],
        )
        self.assertEqual(fixture["action"], Fraction(301, 32))
        self.assertEqual(fixture["tree_density"], Fraction(9, 2))
        self.assertEqual(fixture["coarea_jacobian"], Fraction(153, 4))

    def test_exact_cancellation(self) -> None:
        base = cycle_data(
            [Fraction(1), Fraction(2), Fraction(1), Fraction(1, 2)]
        )
        shifted = cycle_data(
            [Fraction(2), Fraction(1), Fraction(1), Fraction(1, 2)]
        )
        surface = shifted["coarea_jacobian"] / base["coarea_jacobian"]
        density = base["coarea_jacobian"] / shifted["coarea_jacobian"]
        self.assertEqual(surface, Fraction(9, 10))
        self.assertEqual(density, Fraction(10, 9))
        self.assertEqual(surface * density, 1)

    def test_deterministic_builder(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            committed = json.load(handle)
        self.assertEqual(build(), committed)


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.payload = json.load(handle)

    def verify_mutation(self, mutate) -> None:
        changed = copy.deepcopy(self.payload)
        mutate(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_independent_verifier(self) -> None:
        self.assertTrue(verify(CERT_PATH))

    def test_mutation_surface_ratio(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_cycle_tilt"]["surface_jacobian_ratio"].__setitem__(
                "numerator", 8
            )
        )

    def test_mutation_cancellation_product(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_cycle_tilt"]["cancellation_product"].__setitem__(
                "numerator", 2
            )
        )

    def test_mutation_exponent_gap(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_cycle_tilt"]["boltzmann_exponent_gap"].__setitem__(
                "numerator", 5324
            )
        )

    def test_mutation_marginal_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "normalized_lowest_mode_marginal_bound", "PROVED"
            )
        )

    def test_mutation_actual_moment_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment_bound", "PROVED"
            )
        )

    def test_mutation_foundational_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["foundational_dependency_cut"].__setitem__(
                "weakest_base_or_reversal", "PROVED"
            )
        )

    def test_mutation_provenance(self) -> None:
        self.verify_mutation(
            lambda data: data["provenance"]["inputs"][0].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.verify_mutation(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
