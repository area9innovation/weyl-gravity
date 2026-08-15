"""Tests for the all-coupling BT OS kernel obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_all_coupling_os_kernel_obstruction import (
    CERT_PATH,
    build,
    fixture,
)
from reverse_physics.verify_bt_euclidean_all_coupling_os_kernel_obstruction import (
    gap_at_half_length,
    verify,
)


class ExactObstructionTests(unittest.TestCase):
    def test_l6_and_stable_padded_gaps(self) -> None:
        self.assertEqual(fixture(3)["gap"], Fraction(28683, 1024))
        for half_length in (4, 5, 8, 17):
            self.assertEqual(fixture(half_length)["gap"], Fraction(1023, 4))

    def test_independent_time_reconstruction(self) -> None:
        self.assertEqual(gap_at_half_length(3), Fraction(28683, 1024))
        self.assertEqual(gap_at_half_length(9), Fraction(1023, 4))


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

    def test_mutation_l6_gap(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_fixtures"]["L6"][
                "gap_per_spatial_site"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_coupling_scope(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["theorem"].__setitem__(
                "coupling_scope", "lambda=0.4 only"
            )
        )

    def test_mutation_os_disposition(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["scope_disposition"].__setitem__(
                "ordinary_os_at_every_lambda_nonzero_even_L_at_least_6",
                "OPEN",
            )
        )

    def test_mutation_continuum_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["scope_disposition"].__setitem__(
                "continuum_os_for_fixed_cutoff_independent_observables",
                "OBSTRUCTED",
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["scope_disposition"].__setitem__(
                "interacting_uniform_h_minus_one", "BOUNDED"
            )
        )

    def test_mutation_predecessor_hash(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["provenance"]["inputs"][0].__setitem__(
                "sha256", "0" * 64
            )
        )

    def test_mutation_extra_claim(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("lorentzian_transfer", "PROVED")
        )


if __name__ == "__main__":
    unittest.main()
