"""Tests for the exact BT runaway-fiber recentered-width theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_runaway_fiber_width_bound import (
    CERT_PATH,
    aggregate_by_z,
    build,
    curvature_terms,
    direct_curvature,
)
from reverse_physics.verify_bt_euclidean_runaway_fiber_width_bound import verify


class ExactCalculationTests(unittest.TestCase):
    def test_direct_and_laurent_rails_agree(self) -> None:
        terms = curvature_terms()
        for m, u in ((2, -10), (2, -8), (2, 0), (3, -15), (4, -21)):
            aggregate = aggregate_by_z(terms, Fraction(2 ** (4 * m)))
            z = Fraction(2**u) if u >= 0 else Fraction(1, 2 ** (-u))
            laurent = sum(
                (coefficient * z**power for power, coefficient in aggregate.items()),
                Fraction(0),
            )
            self.assertEqual(direct_curvature(m, u), laurent)

    def test_exact_bound_constant(self) -> None:
        self.assertEqual(Fraction(32) - 1 - Fraction(9, 4), Fraction(115, 4))
        self.assertEqual(
            Fraction(1, 1) / (1350 * Fraction(115, 4)),
            Fraction(2, 77625),
        )
        self.assertEqual(
            Fraction(2, 77625) / Fraction(1, 2) ** 2,
            Fraction(8, 77625),
        )
        self.assertLess(Fraction(8, 77625), Fraction(3, 4))

    def test_deterministic_builder(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.assertEqual(build(), json.load(handle))


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

    def test_mutation_laurent_coefficient(self) -> None:
        self.verify_mutation(
            lambda data: data["exact_curvature"]["bivariate_terms"][0].__setitem__(
                "coefficient", 3
            )
        )

    def test_mutation_lower_bound(self) -> None:
        self.verify_mutation(
            lambda data: data["uniform_lower_bound"]["lower_bound"].__setitem__(
                "numerator", 116
            )
        )

    def test_mutation_variance_prefactor(self) -> None:
        self.verify_mutation(
            lambda data: data["conditional_variance"]["rational_prefactor"].__setitem__(
                "numerator", 3
            )
        )

    def test_mutation_center_escape(self) -> None:
        self.verify_mutation(
            lambda data: data["conditional_center_escape"].__setitem__(
                "conclusion", "E_qm[u]<0"
            )
        )

    def test_mutation_all_background_promotion(self) -> None:
        self.verify_mutation(
            lambda data: data["method_disposition"].__setitem__(
                "all_background_uniform_recentered_conditional_variance", "PROVED"
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
