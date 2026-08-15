"""Tests for the BT mixed-mode Witten-tangent gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_mixed_mode_witten_tangent_gate import (
    CERT_PATH,
    build,
    free_fixture,
    reduced_weak_coupling_fixture,
)
from reverse_physics.verify_bt_euclidean_mixed_mode_witten_tangent_gate import (
    decode,
    free_fixture_reconstruction,
    reduced_relative_coefficient,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_free_fixture_reconstruction(self) -> None:
        fixture = free_fixture()
        rebuilt = free_fixture_reconstruction()
        self.assertEqual(rebuilt["relative"], decode(fixture["relative_factor"]))
        self.assertEqual(rebuilt["relative"], Fraction(2309, 2305))
        self.assertGreater(rebuilt["increase"], 0)

    def test_reduced_coefficient(self) -> None:
        for b in (Fraction(0), Fraction(1), Fraction(2), Fraction(5, 3)):
            self.assertEqual(
                reduced_relative_coefficient(b), 4 * (b * b - 2 * b + 2)
            )

    def test_deterministic_resonance_is_lifted(self) -> None:
        fixture = reduced_weak_coupling_fixture()
        self.assertEqual(
            decode(fixture["coefficient_at_deterministic_resonance"]),
            Fraction(52, 9),
        )
        self.assertEqual(decode(fixture["minimum_coefficient"]), 4)


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

    def test_mutation_free_fixture(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_free_fixture"]["relative_factor"].__setitem__(
                "numerator", 1
            )
        )

    def test_mutation_weak_coefficient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["reduced_interacting_theorem"].__setitem__(
                "weak_expansion", "lambda^2 R=1"
            )
        )

    def test_mutation_method_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "interacting_h_minus_one_bound", "PROVED"
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
