"""Tests for the exact BT orthogonal-Hessian obstruction certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_orthogonal_hessian_block_obstruction import (
    CERT_PATH,
    build,
    residual_for_odd_count,
)
from reverse_physics.verify_bt_euclidean_orthogonal_hessian_block_obstruction import (
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def test_residual_classes(self) -> None:
        self.assertEqual(
            [residual_for_odd_count(index) for index in range(5)],
            [
                Fraction(-7, 2),
                Fraction(-77, 72),
                Fraction(49, 36),
                Fraction(91, 24),
                Fraction(56, 9),
            ],
        )

    def test_negative_hessian_decomposition(self) -> None:
        even = 16 * (Fraction(81, 4) + Fraction(-7, 2) * Fraction(9, 2))
        one_odd = 64 * Fraction(-77, 72) * Fraction(32, 9)
        self.assertEqual(even, 72)
        self.assertEqual(one_odd, Fraction(-19712, 81))
        self.assertEqual(even + one_odd, Fraction(-13880, 81))

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

    def test_mutation_hessian(self) -> None:
        self.verify_mutation(
            lambda data: data["cell_calculation"].__setitem__(
                "directional_hessian", {"numerator": -13879, "denominator": 81}
            )
        )

    def test_mutation_orthogonality(self) -> None:
        self.verify_mutation(
            lambda data: data["lowest_mode_orthogonality"].__setitem__(
                "status", "OPEN"
            )
        )

    def test_mutation_replication(self) -> None:
        self.verify_mutation(
            lambda data: data["replication"].__setitem__(
                "status", "FINITE_VOLUME_ONLY"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.verify_mutation(
            lambda data: data.__setitem__(
                "dependency_tags", ["LOCAL-ALGEBRAIC", "LORENTZIAN-CAUSAL"]
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
