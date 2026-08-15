"""Tests for the BT heat-bath influence symbol gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_heat_bath_influence_symbol_gate import (
    CERT_PATH,
    bilaplacian_origin_row,
    build,
    mode_fixture,
)
from reverse_physics.verify_bt_euclidean_heat_bath_influence_symbol_gate import (
    independent_fixture,
    verify,
)


class ExactKernelTests(unittest.TestCase):
    def test_origin_row(self) -> None:
        row = bilaplacian_origin_row(4)
        self.assertEqual(row[(0, 0, 0, 0)], 72)
        self.assertEqual(sum(row.values()), 0)
        self.assertEqual(
            sum(abs(value) for site, value in row.items() if site != (0, 0, 0, 0)),
            184,
        )

    def test_independent_fixture(self) -> None:
        producer = mode_fixture(4)
        verifier = independent_fixture(4)
        self.assertEqual(producer["diagonal"], verifier["diagonal"])
        self.assertEqual(producer["lowest_heat_bath_rate"], Fraction(1, 18))
        self.assertEqual(verifier["checker_response"], Fraction(-23, 9))


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

    def test_mutation_absolute_row_sum(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["absolute_influence_obstruction"][
                "normalized_absolute_row_sum"
            ].__setitem__("numerator", 22)
        )

    def test_mutation_checkerboard(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_l4_fixture"][
                "checkerboard_simultaneous_response"
            ].__setitem__("numerator", -22)
        )

    def test_mutation_signed_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "signed_fourier_multiscale_influence", "PROVED"
            )
        )

    def test_mutation_global_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "interacting_h_minus_one_bound", "PROVED"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
