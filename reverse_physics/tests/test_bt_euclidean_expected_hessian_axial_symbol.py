"""Tests for the BT expected-Hessian axial symbol certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_expected_hessian_axial_symbol import (
    CERT_PATH,
    build,
    fixture,
)
from reverse_physics.bt_euclidean_hessian_symbol_experiment import (
    local_orbit_coefficients,
)
from reverse_physics.bt_euclidean_lattice_pilot import periodic_neighbors
from reverse_physics.bt_euclidean_lattice_step_scaling_experiment import (
    independent_residuals,
)
from reverse_physics.verify_bt_euclidean_expected_hessian_axial_symbol import (
    independent_fixture,
    verify,
)


class ExactSymbolTests(unittest.TestCase):
    def test_exact_fixture_has_nonzero_alpha(self) -> None:
        produced = fixture()
        independent = independent_fixture()
        self.assertEqual(produced["alpha"], Fraction(3, 2))
        self.assertEqual(
            independent,
            (Fraction(-133, 12), Fraction(59, 48), Fraction(7, 3), Fraction(3, 2), Fraction(13, 12)),
        )

    def test_vacuum_recovers_bilaplacian_symbol(self) -> None:
        length = 6
        dimensions = 4
        field = [0.0] * (length**dimensions)
        residual = independent_residuals(
            field, 0.4, periodic_neighbors(length, dimensions)
        )
        coefficients = local_orbit_coefficients(
            field, residual, 0.4, length, dimensions
        )
        self.assertEqual(coefficients, {"b": -16.0, "c": 1.0, "d": 2.0, "alpha": 0.0})


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

    def test_mutation_fixture_alpha(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_fixture"]["alpha"].__setitem__("numerator", 2)
        )

    def test_mutation_uniform_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["uniform_full_gibbs_bounds"]["C_H"].__setitem__("numerator", 1)
        )

    def test_mutation_observation(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["finite_volume_diagnostic"]["summaries"][0].__setitem__("mean_alpha", 0.0)
        )

    def test_mutation_conditioned_score_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__("conditioned_background_score_bound", "PROVED")
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "BOUNDED")
        )

    def test_mutation_lorentzian_claim(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("lorentzian_transfer", "PROVED")
        )


if __name__ == "__main__":
    unittest.main()
