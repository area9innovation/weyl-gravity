"""Tests for the BT affine virial and actual action-density theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_affine_virial_action_density import (
    CERT_PATH,
    build,
    exp_seven_tenths_lower_bound,
    log_two_lower_bound,
    scalar_fixture,
)
from reverse_physics.verify_bt_euclidean_affine_virial_action_density import (
    reconstruct_fixture,
    verify,
)


class ExactCalculationTests(unittest.TestCase):
    def test_log_bracket(self) -> None:
        self.assertEqual(
            log_two_lower_bound(), Fraction(155685007, 232792560)
        )
        self.assertGreater(log_two_lower_bound(), Fraction(2, 3))
        self.assertEqual(
            exp_seven_tenths_lower_bound(), Fraction(482921, 240000)
        )
        self.assertGreater(exp_seven_tenths_lower_bound(), 2)

    def test_scalar_fixtures(self) -> None:
        rows = [
            scalar_fixture((Fraction(2),) + (Fraction(1),) * 7),
            scalar_fixture((Fraction(1, 2),) * 8),
            scalar_fixture((Fraction(4),) + (Fraction(1, 4),) * 7),
        ]
        rebuilt = [reconstruct_fixture(row) for row in rows]
        self.assertEqual(
            [value["residual"] > 0 for value in rebuilt],
            [True, False, False],
        )
        self.assertLess(rebuilt[1]["coefficient"], 0)
        self.assertGreater(rebuilt[2]["coefficient"], 0)

    def test_exact_action_density_constants(self) -> None:
        defect = Fraction(488, 5)
        coupling = Fraction(2, 5)
        action_density = defect / 2 + coupling * coupling / 2
        self.assertEqual(action_density, Fraction(1222, 25))
        self.assertEqual(1 + action_density, Fraction(1247, 25))
        self.assertEqual(16 * 8 * 8 * action_density, Fraction(1251328, 25))


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

    def test_mutation_affine_constant(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["pointwise_affine_virial_theorem"].__setitem__(
                "q8_rational_bound", "D>=2A-97*N"
            )
        )

    def test_mutation_action_density(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["actual_gibbs_action_density"][
                "lambda_point_four_uniform_action_density_bound"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment_bound", "PROVED"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(
                1, "LORENTZIAN-CAUSAL"
            )
        )

    def test_mutation_provenance(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["provenance"]["inputs"][0].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
