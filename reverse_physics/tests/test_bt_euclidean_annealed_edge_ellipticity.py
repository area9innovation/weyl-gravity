"""Tests for the BT actual-Gibbs annealed edge-ellipticity theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_annealed_edge_ellipticity import (
    ABSOLUTE_JUMP_EXP_BOUND,
    CERT_PATH,
    CURRENT_FIRST_MOMENT_BOUND,
    RATIO_SECOND_MOMENT_BOUND,
    build,
    cycle_fixture,
)
from reverse_physics.verify_bt_euclidean_annealed_edge_ellipticity import (
    decode,
    reconstruct_cycle,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_constants(self) -> None:
        self.assertEqual(RATIO_SECOND_MOMENT_BOUND, Fraction(8088, 25))
        self.assertEqual(ABSOLUTE_JUMP_EXP_BOUND, Fraction(16176, 25))
        self.assertEqual(CURRENT_FIRST_MOMENT_BOUND, Fraction(8932, 25))

    def test_independent_cycle_reconstruction(self) -> None:
        fixture = cycle_fixture()
        rebuilt = reconstruct_cycle(fixture["omega"])
        self.assertEqual(rebuilt["residual"], [decode(x) for x in fixture["residual"]])
        self.assertEqual(len(rebuilt["directed_edges"]), 8)

    def test_pointwise_envelopes(self) -> None:
        rebuilt = reconstruct_cycle(cycle_fixture()["omega"])
        for row in rebuilt["directed_edges"]:
            self.assertLessEqual(row["ratio_square"], row["pointwise_ratio_square_envelope"])
            self.assertLessEqual(row["exp_twice_absolute_jump"], row["two_orientation_envelope"])


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
        mutate(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_ratio_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["theorem"]["bounds"].__setitem__(
                "directed_ratio_second_moment", "E[w_xy^2]<=1"
            )
        )

    def test_mutation_fixture(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_fixture"]["omega"][0].__setitem__("numerator", 2)
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
