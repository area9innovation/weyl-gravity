"""Tests for the BT Schwinger--Dyson mode-route obstruction certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_schwinger_dyson_mode_obstruction import (
    CERT_PATH,
    build,
    negative_cycle_laplacian,
    reduced_forms,
)
from reverse_physics.verify_bt_euclidean_schwinger_dyson_mode_obstruction import (
    full_lattice_forms,
    verify,
)


CENTER = (-8, 8, -2, -8, 2, 8)
DIRECTION = (2, 1, -1, -2, -1, 1)


class ExactCalculationTests(unittest.TestCase):
    def test_reduced_exact_counterexample(self) -> None:
        forms = reduced_forms(CENTER, DIRECTION)
        self.assertEqual(negative_cycle_laplacian(DIRECTION), DIRECTION)
        self.assertEqual(forms["center_direction_dot"], 16)
        self.assertEqual(forms["direction_norm_squared"], 12)
        self.assertEqual(forms["free_directional_action"], 16)
        self.assertEqual(
            forms["directional_action"],
            Fraction(-36885875918835948063, 2147483648),
        )
        self.assertLess(forms["directional_action"], 0)

    def test_full_lattice_checker_is_distinct(self) -> None:
        forms = full_lattice_forms(CENTER, DIRECTION)
        reduced = reduced_forms(CENTER, DIRECTION)
        for key in (
            "action",
            "directional_action",
            "free_directional_action",
            "center_direction_dot",
            "direction_norm_squared",
        ):
            self.assertEqual(forms[key], 216 * reduced[key])
        self.assertEqual(forms["lowest_mode_residual"], 0)

    def test_lambda_point_four_lowest_mode_coefficient(self) -> None:
        self.assertEqual(Fraction(128) * Fraction(2, 5) ** 2, Fraction(512, 25))


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
            lambda cert: cert["exact_lowest_mode_counterexample"][
                "spatially_constant_time_center"
            ].__setitem__(0, -7)
        )

    def test_mutation_directional_action(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_lowest_mode_counterexample"]["full_lattice"][
                "nonlinear_directional_action"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_fourier_constant(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["all_volume_quartic_coercivity"][
                "lowest_axial_fourier_consequence"
            ]["lambda_0p4_coefficient"].__setitem__("numerator", 511)
        )

    def test_mutation_method_disposition(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "interacting_h_minus_one_second_moment_bound", "PROVED"
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
