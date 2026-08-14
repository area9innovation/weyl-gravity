"""Tests for the exact BT conditional-mass escape obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_conditional_mass_escape_obstruction import (
    CERT_PATH,
    build,
    cycle_action,
    fiber_coefficients,
    theorem_constants,
)
from reverse_physics.verify_bt_euclidean_conditional_mass_escape_obstruction import (
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = (-1, -1, 1, -3, 3, 1)
        self.h = (2, 1, -1, -2, -1, 1)

    def test_orthogonal_family(self) -> None:
        self.assertEqual(sum(self.a), 0)
        self.assertEqual(sum(self.h), 0)
        self.assertEqual(sum(x * y for x, y in zip(self.a, self.h)), 0)

    def test_m2_candidate_and_threshold_actions(self) -> None:
        candidate = fiber_coefficients(2, -8, self.a, self.h)
        threshold = fiber_coefficients(2, -2, self.a, self.h)
        constants = theorem_constants(2)
        self.assertLessEqual(cycle_action(candidate), constants["well_upper"])
        self.assertGreaterEqual(
            cycle_action(threshold), constants["center_lower"]
        )

    def test_all_m_energy_gap(self) -> None:
        for m in range(2, 14):
            constants = theorem_constants(m)
            self.assertGreater(
                constants["center_lower"], constants["well_upper"]
            )

    def test_all_m_tail_exponent(self) -> None:
        for m in range(2, 14):
            constants = theorem_constants(m)
            self.assertLessEqual(constants["tail_binary_exponent"], -m)

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
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        mutate(changed)
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

    def test_mutation_candidate_action(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_m2_fixture"]["candidate_cycle_action"].__setitem__(
                "numerator", 1
            )
        )

    def test_mutation_tail_exponent(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_m2_fixture"].__setitem__(
                "binary_tail_exponent", -2
            )
        )

    def test_mutation_tail_probability_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["all_m_comparison"].__setitem__(
                "tail_probability_bound", "q_m({u>=-m})<=1"
            )
        )

    def test_mutation_recentered_variance_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "uniform_recentered_conditional_variance", "PROVED"
            )
        )

    def test_mutation_annealed_center_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "annealed_center_second_moment", "PROVED"
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "PROVED"
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
