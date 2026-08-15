"""Tests for the BT Gauss-Newton Witten parametrix obstruction."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_gauss_newton_witten_parametrix_obstruction import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_gauss_newton_witten_parametrix_obstruction import (
    verify,
)


class GaussNewtonWittenParametrixTests(unittest.TestCase):
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

    def test_mutated_vacuum_coefficient_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_fixtures"]["vacuum_full"]
            ["L1_image_fourier_coefficients"]["lowest_cosine"].__setitem__(
                "numerator", 50
            )
        )

    def test_mutated_asymmetric_q_mixing_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_fixtures"]["asymmetric_full"]
            ["defect_fourier_coefficients"]["checkerboard"].__setitem__(
                "numerator", 0
            )
        )

    def test_mutated_centered_sine_mixing_is_rejected(self) -> None:
        self.reject(
            lambda data: data["exact_fixtures"]["asymmetric_centered"]
            ["defect_fourier_coefficients"]["lowest_sine"].__setitem__(
                "numerator", 0
            )
        )

    def test_full_candidate_promotion_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "full_action_gauss_newton_pointwise_parametrix", "PROVED"
            )
        )

    def test_corrected_candidate_obstruction_is_rejected(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "connection_corrected_or_nonlocal_witten_parametrix",
                "OBSTRUCTED",
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
