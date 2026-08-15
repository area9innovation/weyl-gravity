"""Tests for finite repaired BT multibubble compactness."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_finite_multibubble_compactness import (
    CERT_PATH,
    build,
    nonzero_fixture,
    weak_endpoint_quotient,
)
from reverse_physics.verify_bt_euclidean_finite_multibubble_compactness import (
    reconstruct_fixture,
    reconstruct_jet,
    reconstruct_weak_limit,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_repaired_jet(self) -> None:
        jet = reconstruct_jet()
        self.assertEqual(jet["quartic"], 0)
        self.assertEqual(jet["sextic"], Fraction(-8, 45))

    def test_nonzero_fixture(self) -> None:
        producer = nonzero_fixture()
        rebuilt = reconstruct_fixture()
        self.assertEqual(rebuilt["field"], Fraction(4, 3))
        self.assertEqual(rebuilt["laplacian"], Fraction(8, 3))
        self.assertEqual(rebuilt["q"], Fraction(-32, 9))
        self.assertEqual(producer["q_0"]["numerator"], -32)

    def test_weak_endpoint(self) -> None:
        self.assertEqual(weak_endpoint_quotient(), Fraction(512, 17))
        self.assertEqual(reconstruct_weak_limit(), Fraction(512, 17))


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

    def test_mutation_zero_count(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["crystal_fixture"].__setitem__("zero_count", 15)
        )

    def test_mutation_weak_limit(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["finite_and_weak_endpoints"]["crystal_weak_value"].__setitem__(
                "numerator", 511
            )
        )

    def test_mutation_growing_gas_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "growing_number_bubble_gas", "RULED_OUT"
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
