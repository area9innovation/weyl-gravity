"""Tests and mutation rail for the BT interacting OS witness preflight."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_os_witness_experiment import (
    reflected_observable,
)
from reverse_physics.bt_euclidean_os_witness_preflight import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_os_witness_preflight import verify


class ObservableTests(unittest.TestCase):
    def test_reflection_formula(self) -> None:
        length, dimensions = 6, 4
        field = []
        for time in range(length):
            field.extend([float(time)] * (length ** (dimensions - 1)))
        positive, reflected, product = reflected_observable(
            field, length, dimensions
        )
        self.assertEqual(positive, 0.0)
        self.assertEqual(reflected, 6.0)
        self.assertEqual(product, 0.0)


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

    def test_mutation_mean(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["runs"][0].__setitem__(
                "mean_reflected_product", 0.0
            )
        )

    def test_mutation_cross_sampler_score(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("cross_sampler_mean_z", 0.0)
        )

    def test_mutation_exact_promotion(self) -> None:
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

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
