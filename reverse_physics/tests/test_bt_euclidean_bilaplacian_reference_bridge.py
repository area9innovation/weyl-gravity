"""Tests for the BT bilaplacian radial-reference bridge certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_bilaplacian_reference_bridge import (
    CERT_PATH,
    alternating_log_two_lower_bound,
    build,
    positive_square_fraction,
)
from reverse_physics.verify_bt_euclidean_bilaplacian_reference_bridge import (
    full_lattice_hessian_forms,
    verify,
)


CENTER = (-3, 0, 0, -3, 3, 3)
DIRECTION = (-1, -1, 1, 1, 1, -1)


class ExactCalculationTests(unittest.TestCase):
    def test_positive_part_lemma_fixtures(self) -> None:
        for values in ((-3, 1, 1, 1), (-5, 1, 1, 1, 1, 1), (-7, -2, 3, 3, 3)):
            self.assertEqual(sum(values), 0)
            self.assertGreaterEqual(positive_square_fraction(values), Fraction(1, len(values)))

    def test_alternating_log_lower_bound(self) -> None:
        value = alternating_log_two_lower_bound(20)
        self.assertEqual(value, Fraction(155685007, 232792560))
        self.assertGreater(value, Fraction(2, 3))

    def test_full_lattice_hessian(self) -> None:
        forms = full_lattice_hessian_forms(CENTER, DIRECTION)
        self.assertEqual(forms["actual_hessian"], 243)
        self.assertEqual(forms["center_bilaplacian_integer"], 216 * 252)
        self.assertEqual(forms["direction_bilaplacian"], 216 * 16)
        self.assertEqual(forms["bilaplacian_cross"], 0)


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

    def test_mutation_envelope(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["all_volume_bilaplacian_envelope"].__setitem__("first_bound", "A>=0")
        )

    def test_mutation_actual_hessian(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["convex_transfer_obstruction"]["actual_directional_hessian_full"].__setitem__("numerator", 244)
        )

    def test_mutation_reference_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["normalized_radial_reference"]["lambda_0p4_q8_bound"]["rational_prefactor"].__setitem__("numerator", 4)
        )

    def test_mutation_disposition(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["disposition"].__setitem__("actual_interacting_h_minus_one_second_moment_bound", "PROVED")
        )

    def test_mutation_dependency_tag(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(1, "LORENTZIAN-CAUSAL")
        )

    def test_mutation_provenance(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64)
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
