"""Tests for the BT flat-potential Piola/Ward cancellation."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_flat_potential_piola_ward_cancellation import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_flat_potential_piola_ward_cancellation import (
    verify,
)


class FlatPotentialPiolaWardTests(unittest.TestCase):
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

    def test_mutated_jacobian_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_cycle_fixture"][
                "oriented_jacobian_determinant"
            ].__setitem__("numerator", -124)
        )

    def test_mutated_piola_divergence_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_cycle_fixture"][
                "piola_divergence"
            ].__setitem__("numerator", -62)
        )

    def test_mutated_action_score_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_cycle_fixture"][
                "action_score"
            ].__setitem__("numerator", -74)
        )

    def test_missing_resolvent_formula_is_rejected(self) -> None:
        self.reject(
            lambda data: data["ground_state_resolvent_interface"].__setitem__(
                "potential_gradient", "unspecified"
            )
        )

    def test_method_obstruction_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "induced_determinant_ward_as_new_estimate", "PROVED"
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
