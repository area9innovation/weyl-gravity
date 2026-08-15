"""Tests for the BT Witten one-form Schur-gate certificate."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_witten_one_form_schur_gate import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_witten_one_form_schur_gate import (
    verify,
)


class WittenOneFormSchurGateTests(unittest.TestCase):
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

    def test_mutated_symbolic_coefficient_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_symbolic_fixture"]["L1_gradient"][0][0]
            ["coefficient"].__setitem__("numerator", 999)
        )

    def test_mutated_hessian_determinant_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_symbolic_fixture"]
            ["hessian_determinant_at_origin"].__setitem__("numerator", 10)
        )

    def test_witten_factorization_removal_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "witten_one_form_factorization", "OPEN"
            )
        )

    def test_pointwise_no_go_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "pointwise_negative_hessian_as_witten_no_go", "PROVED"
            )
        )

    def test_coercivity_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "volume_uniform_witten_schur_coercivity", "PROVED"
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
