"""Tests and mutation rail for the BT convexity-route obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_uniform_convexity_obstruction import (
    CERT_PATH,
    build,
    expected_hessian,
    expected_ratio,
    hessian_and_free_form,
)
from reverse_physics.verify_bt_euclidean_uniform_convexity_obstruction import (
    full_lattice_forms,
    symbolic_reduced_hessian,
    verify,
)


class ExactFamilyTests(unittest.TestCase):
    def test_closed_form_for_extended_exact_range(self) -> None:
        for parameter in range(1, 33):
            hessian, free_form = hessian_and_free_form(parameter)
            self.assertEqual(hessian, expected_hessian(parameter))
            self.assertEqual(free_form, 16)
            self.assertEqual(hessian / free_form, expected_ratio(parameter))

    def test_full_lattice_checker_is_distinct(self) -> None:
        for parameter in (1, 4, 12):
            hessian, free_form = full_lattice_forms(parameter)
            self.assertEqual(hessian, 216 * expected_hessian(parameter))
            self.assertEqual(free_form, 216 * 16)

    def test_ratio_has_exact_zero_limit_bound(self) -> None:
        for parameter in range(1, 129):
            ratio = expected_ratio(parameter)
            self.assertGreater(ratio, 0)
            self.assertLessEqual(ratio, Fraction(1, 2**parameter))

    def test_symbolic_laurent_derivation(self) -> None:
        self.assertEqual(
            symbolic_reduced_hessian(),
            {-1: Fraction(8), -2: Fraction(8)},
        )


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

    def test_mutation_center(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_degenerating_family"]["fixtures"][0][
                "time_center"
            ].__setitem__(0, -2)
        )

    def test_mutation_ratio(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_degenerating_family"]["fixtures"][4][
                "ratio"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_method_disposition(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "interacting_h_minus_one_second_moment_bound", "OBSTRUCTED"
            )
        )

    def test_mutation_dependency_tag(self) -> None:
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

    def test_mutation_extra_top_level_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
