"""Tests for the BT mixed-mode sharp-gradient obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_mixed_mode_sharp_gradient_obstruction import (
    CERT_PATH,
    build,
    continuum_fixture,
    lattice_fixture,
)
from reverse_physics.verify_bt_euclidean_mixed_mode_sharp_gradient_obstruction import (
    continuum_reconstruction,
    decode,
    expected_lattice_gap_coefficient,
    formal_lattice_gap_coefficient,
    lattice_fixture_reconstruction,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_continuum_fourier_reconstruction(self) -> None:
        fixture = continuum_fixture()
        rebuilt = continuum_reconstruction()
        self.assertEqual(rebuilt["residual_norm"], decode(fixture["residual_norm_squared"]))
        self.assertEqual(rebuilt["euler_norm"], decode(fixture["euler_norm_squared"]))
        self.assertLess(rebuilt["gap"], 0)

    def test_formal_lattice_coefficient(self) -> None:
        for mixed in (Fraction(0), Fraction(1), Fraction(2), Fraction(5, 3)):
            self.assertEqual(
                formal_lattice_gap_coefficient(mixed),
                expected_lattice_gap_coefficient(mixed),
            )

    def test_exact_lattice_fixture(self) -> None:
        fixture = lattice_fixture()
        rebuilt = lattice_fixture_reconstruction(fixture["omega_table"])
        self.assertEqual(
            rebuilt["residual_norm"],
            decode(fixture["residual_norm_squared_per_transverse_copy"]),
        )
        self.assertEqual(
            rebuilt["gradient_norm"],
            decode(fixture["gradient_norm_squared_per_transverse_copy"]),
        )
        self.assertLess(rebuilt["ratio"], Fraction(35, 102))

    def test_pell_bridge(self) -> None:
        self.assertEqual(577**2 - 2 * 408**2, 1)
        self.assertEqual(6 - Fraction(4 * 577, 408), Fraction(35, 102))


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

    def test_mutation_continuum_fixture(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_continuum_fixture"]["euler_norm_squared"].__setitem__(
                "numerator", 1
            )
        )

    def test_mutation_lattice_table(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_lattice_fixture"]["omega_table"][0].__setitem__(0, 1)
        )

    def test_mutation_method_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "interacting_h_minus_one_bound", "PROVED"
            )
        )

    def test_mutation_lattice_coefficient(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["lattice_theorem"].__setitem__(
                "coefficient", "C_L(b)=0"
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
