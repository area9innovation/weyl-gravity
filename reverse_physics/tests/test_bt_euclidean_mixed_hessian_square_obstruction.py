"""Tests for the BT mixed-Hessian-square obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_mixed_hessian_square_obstruction import (
    CERT_PATH,
    build,
    origin_hessian_row,
    shell_sums,
)
from reverse_physics.verify_bt_euclidean_mixed_hessian_square_obstruction import (
    independent_hessian_row,
    verify,
)


class ExactStencilTests(unittest.TestCase):
    def test_origin_row(self) -> None:
        row = origin_hessian_row()
        self.assertEqual(len(row), 41)
        self.assertEqual(sum(row.values(), Fraction()), 0)
        self.assertEqual(
            shell_sums(row),
            {
                -2: Fraction(3, 16),
                -1: Fraction(-40),
                1: Fraction(-21),
                2: Fraction(3, 4),
            },
        )

    def test_independent_derivative_row(self) -> None:
        self.assertEqual(origin_hessian_row(), independent_hessian_row())


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

    def test_mutation_first_moment(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["periodic_fixture"]["first_axial_moment"].__setitem__(
                "numerator", 160
            )
        )

    def test_mutation_shell(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["periodic_fixture"]["axial_shell_sums"]["-1"].__setitem__(
                "numerator", -39
            )
        )

    def test_mutation_signed_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "signed_conditional_covariance_response", "PROVED"
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
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
