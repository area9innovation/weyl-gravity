"""Tests for the growing repaired BT multibubble crystal."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_multibubble_crystal_scaling import (
    CERT_PATH,
    build,
    scaling_fixture,
)
from reverse_physics.verify_bt_euclidean_multibubble_crystal_scaling import (
    reconstruct_k3,
    verify,
)


class ExactScalingTests(unittest.TestCase):
    def test_k3_fixture(self) -> None:
        producer = scaling_fixture(3)
        verifier = reconstruct_k3()
        self.assertEqual(producer["zero_count"], 1296)
        self.assertEqual(producer["quotient_factor"], 81)
        self.assertEqual(verifier["weak"], Fraction(41472, 17))
        self.assertEqual(verifier["sextic"], Fraction(-72, 5))

    def test_invalid_frequency(self) -> None:
        with self.assertRaises(ValueError):
            scaling_fixture(0)


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

    def test_mutation_quotient_factor(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_fixture_K3"].__setitem__("quotient_factor", 80)
        )

    def test_mutation_scaling_identity(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["operator_scaling"].__setitem__(
                "euler", "E_K,m(x)=K^3*E_16,M(K*x)"
            )
        )

    def test_mutation_gas_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "irregular_or_correlated_growing_gas", "RULED_OUT"
            )
        )

    def test_mutation_witten_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "volume_uniform_witten_coercivity", "PROVED"
            )
        )

    def test_mutation_dependency(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(2, "LORENTZIAN-CAUSAL")
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
