"""Tests for the exact BT centered-fiber domination obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_centered_fiber_domination_obstruction import (
    CERT_PATH,
    action_polynomial,
    build,
    evaluate,
    residual_polynomials,
)
from reverse_physics.verify_bt_euclidean_centered_fiber_domination_obstruction import (
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.h = (2, 1, -1, -2, -1, 1)
        self.background = (-1, -1, 1, -3, 3, 1)
        self.shifted = tuple(
            left - right for left, right in zip(self.background, self.h)
        )

    def test_orthogonal_lowest_mode(self) -> None:
        self.assertEqual(sum(self.background), 0)
        self.assertEqual(sum(self.h), 0)
        self.assertEqual(
            sum(left * right for left, right in zip(self.background, self.h)),
            0,
        )
        self.assertEqual(sum(value * value for value in self.h), 12)

    def test_background_residual_row_supplies_lower_bound(self) -> None:
        residuals = residual_polynomials(self.background)
        self.assertEqual(residuals[3], {6: 1, 4: 1, 0: -2})

    def test_action_leading_powers(self) -> None:
        background = action_polynomial(self.background)
        shifted = action_polynomial(self.shifted)
        self.assertEqual(max(background), 12)
        self.assertEqual(background[12], Fraction(1, 2))
        self.assertEqual(max(shifted), 10)
        self.assertEqual(shifted[10], Fraction(1, 2))

    def test_n1_exact_actions(self) -> None:
        background = evaluate(action_polynomial(self.background), Fraction(2))
        shifted = evaluate(action_polynomial(self.shifted), Fraction(2))
        self.assertEqual(background, Fraction(25038513, 8192))
        self.assertEqual(shifted, Fraction(1970877, 2048))
        self.assertEqual(shifted / background, Fraction(2627836, 8346171))

    def test_ratio_bound_on_exact_samples(self) -> None:
        background = action_polynomial(self.background)
        shifted = action_polynomial(self.shifted)
        for n in range(1, 7):
            x = Fraction(2**n)
            self.assertLessEqual(
                evaluate(shifted, x) / evaluate(background, x),
                Fraction(9, 4 * 4**n),
            )

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

    def test_mutation_background_vector(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_orthogonal_family"][
                "background_coefficients"
            ].__setitem__(0, 0)
        )

    def test_mutation_leading_action_term(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_orthogonal_family"][
                "background_action_laurent_polynomial"
            ][0]["coefficient"].__setitem__("numerator", 2)
        )

    def test_mutation_ratio_bound_constant(self) -> None:
        self.verify_mutation(
            lambda data: data["scalable_action_obstruction"][
                "scaled_upper_coefficient"
            ].__setitem__("numerator", 554)
        )

    def test_mutation_full_lattice_fixture(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_n1_fixture"][
                "full_lattice_background_action"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_evenness(self) -> None:
        self.verify_mutation(
            lambda data: data["integrated_marginal_symmetry"].__setitem__(
                "theorem", "m_h(t)<=m_h(0)"
            )
        )

    def test_mutation_annealed_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "annealed_or_recentered_fiber_ratio_bound", "PROVED"
            )
        )

    def test_mutation_second_moment_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "normalized_lowest_mode_second_moment_bound", "PROVED"
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment_bound", "PROVED"
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
