"""Tests for the BT flat-potential determinant pushforward certificate."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_flat_potential_determinant_pushforward import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_flat_potential_determinant_pushforward import (
    verify,
)


class FlatPotentialDeterminantPushforwardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def reject(self, mutation) -> None:
        candidate = copy.deepcopy(self.certificate)
        mutation(candidate)
        ok, failures = verify(candidate)
        self.assertFalse(ok)
        self.assertTrue(failures)

    def test_generated_certificate_is_current(self) -> None:
        self.assertEqual(build(), self.certificate)

    def test_independent_verifier_accepts(self) -> None:
        ok, failures = verify(self.certificate)
        self.assertTrue(ok, failures)

    def test_certificate_has_exact_dependency_tags(self) -> None:
        self.assertEqual(
            self.certificate["dependency_tags"],
            ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        )

    def test_mutated_pseudodeterminant_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_cycle_fixture"]["pseudodeterminant"].__setitem__(
                "numerator", 126
            )
        )

    def test_mutated_surface_jacobian_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_cycle_fixture"]["graph_surface_jacobian"].__setitem__(
                "numerator", 35
            )
        )

    def test_mutated_flat_factor_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_cycle_fixture"]["flat_density_factor"].__setitem__(
                "numerator", 5
            )
        )

    def test_missing_determinant_formula_is_rejected(self) -> None:
        self.reject(
            lambda data: data["flat_normalized_pushforward"].__setitem__(
                "density", "Gaussian"
            )
        )

    def test_uniform_estimate_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "nonconvex_determinant_or_resolvent_estimate", "PROVED"
            )
        )

    def test_mutated_negative_curvature_is_rejected(self) -> None:
        self.reject(
            lambda data: data[
                "exact_path_three_convexity_obstruction"
            ]["full_effective_potential_second_derivative"].__setitem__(
                "numerator", 1
            )
        )

    def test_h_minus_one_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "PROVED"
            )
        )

    def test_lorentzian_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "lorentzian_transfer", "ESTABLISHED"
            )
        )


if __name__ == "__main__":
    unittest.main()
