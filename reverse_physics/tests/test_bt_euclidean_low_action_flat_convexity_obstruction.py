"""Tests for the BT low-action flat-convexity obstruction certificate."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_low_action_flat_convexity_obstruction import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_low_action_flat_convexity_obstruction import (
    verify,
)


class LowActionFlatConvexityObstructionTests(unittest.TestCase):
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

    def test_dependency_tags_are_exact(self) -> None:
        self.assertEqual(
            self.certificate["dependency_tags"],
            ["LOCAL-ALGEBRAIC", "EUCLIDEAN-SPECTRAL"],
        )

    def test_mutated_action_density_is_rejected(self) -> None:
        self.reject(
            lambda data: data["low_action_statement"]["action_density"].__setitem__(
                "numerator", 8001
            )
        )

    def test_mutated_ground_entry_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_longitudinal_fixture"]["omega"][0].__setitem__(
                "numerator", 5
            )
        )

    def test_mutated_second_eigenvalue_derivative_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_longitudinal_fixture"]
            ["lowest_eigenvalue_second_derivative"].__setitem__("numerator", -1)
        )

    def test_mutated_logdet_curvature_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_longitudinal_fixture"]
            ["log_pseudodeterminant_second_derivative"].__setitem__(
                "numerator", -1
            )
        )

    def test_mutated_transverse_bound_is_rejected(self) -> None:
        self.reject(
            lambda data: data["transverse_block_bound"]
            ["summed_curvature_upper_bound"].__setitem__("numerator", 1)
        )

    def test_mutated_full_upper_bound_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_longitudinal_fixture"]
            ["full_four_dimensional_curvature_upper_bound"].__setitem__(
                "numerator", 1
            )
        )

    def test_h_minus_one_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "PROVED"
            )
        )

    def test_bad_volume_sequence_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "controlled_bad_volume_sequence_for_actual_moment", "PROVED"
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
