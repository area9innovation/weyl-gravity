"""Tests and mutation rail for the BT free reconstruction obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_free_reconstruction_obstruction import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_free_reconstruction_obstruction import (
    verify,
)


class ExactProducerTests(unittest.TestCase):
    def test_exact_witness_and_uniform_bound(self) -> None:
        certificate = build()
        witness = certificate["finite_volume_os_obstruction"]
        self.assertEqual(
            witness["four_dimensional_slice_average_reflected_norm"],
            {"numerator": -1, "denominator": 1296},
        )
        self.assertEqual(sum(witness["coefficients"]), 0)
        self.assertEqual(
            certificate["free_volume_uniform_estimate"]["uniform_result"]["bound"],
            {"numerator": 15, "denominator": 32},
        )

    def test_shell_count_formula(self) -> None:
        for radius in range(1, 50):
            direct = (2 * radius + 1) ** 4 - (2 * radius - 1) ** 4
            self.assertEqual(direct, 64 * radius ** 3 + 16 * radius)
            self.assertGreaterEqual(
                Fraction(direct, 256 * radius ** 6),
                Fraction(1, 4 * radius ** 3),
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

    def test_mutation_reflected_norm(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["finite_volume_os_obstruction"][
                "four_dimensional_slice_average_reflected_norm"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_uniform_bound(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["free_volume_uniform_estimate"]["uniform_result"][
                "bound"
            ].__setitem__("numerator", 16)
        )

    def test_mutation_lambda_0p4_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["disposition"].__setitem__(
                "ordinary_os_reflection_positivity_at_lambda_0p4",
                "OBSTRUCTED",
            )
        )

    def test_mutation_lorentzian_tag(self) -> None:
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
