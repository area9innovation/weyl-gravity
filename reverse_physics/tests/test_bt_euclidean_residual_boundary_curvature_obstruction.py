"""Tests for the exact BT residual-boundary curvature obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_residual_boundary_curvature_obstruction import (
    CERT_PATH,
    build,
    cycle_family,
)
from reverse_physics.verify_bt_euclidean_residual_boundary_curvature_obstruction import (
    closed_forms,
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def test_q_two_curvature_fixture(self) -> None:
        fixture = cycle_family(Fraction(2))
        self.assertEqual(fixture["pseudoinverse_quadratic"], Fraction(10, 9))
        self.assertEqual(fixture["second_fundamental_value"], Fraction(80, 153))
        self.assertEqual(fixture["trial_normal_curvature"], Fraction(80, 2601))

    def test_q_two_weighted_mean_curvature(self) -> None:
        fixture = cycle_family(Fraction(2))
        self.assertEqual(fixture["mean_curvature"], Fraction(28568, 44217))
        self.assertEqual(fixture["residual_outward_normal"], Fraction(14, 17))
        self.assertEqual(
            fixture["gaussian_weighted_mean_curvature"],
            Fraction(-398039, 88434),
        )

    def test_closed_forms_match_independent_points(self) -> None:
        for q in range(1, 16):
            fixture = cycle_family(Fraction(q))
            formulas = closed_forms(Fraction(q))
            self.assertEqual(fixture["pseudoinverse_quadratic"], formulas["quadratic"])
            self.assertEqual(fixture["trial_normal_curvature"], formulas["trial"])
            self.assertEqual(fixture["mean_curvature"], formulas["mean"])
            self.assertEqual(fixture["residual_outward_normal"], formulas["normal"])
            self.assertEqual(fixture["gaussian_weighted_mean_curvature"], formulas["weighted"])

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

    def test_mutation_trial_curvature(self) -> None:
        self.verify_mutation(
            lambda data: data["lambda_point_four_fixture"][
                "trial_normal_curvature"
            ].__setitem__("numerator", 81)
        )

    def test_mutation_weighted_mean_curvature(self) -> None:
        self.verify_mutation(
            lambda data: data["lambda_point_four_fixture"][
                "gaussian_weighted_mean_curvature"
            ].__setitem__("numerator", 398039)
        )

    def test_mutation_actual_moment_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment_bound", "PROVED"
            )
        )

    def test_mutation_other_inequalities_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "other_boundary_or_intrinsic_inequalities", "OBSTRUCTED"
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
