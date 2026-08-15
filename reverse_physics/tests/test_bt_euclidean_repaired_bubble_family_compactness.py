"""Tests for repaired BT bubble-family compactness."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_repaired_bubble_family_compactness import (
    CERT_PATH,
    build,
    endpoint_fixture,
    weak_endpoint_quotient,
)
from reverse_physics.verify_bt_euclidean_repaired_bubble_family_compactness import (
    reconstruct_nonzero_fixture,
    reconstruct_weak_quotient,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_nonzero_endpoint_fixture(self) -> None:
        producer = endpoint_fixture()
        rebuilt = reconstruct_nonzero_fixture()
        self.assertEqual(rebuilt["field"], Fraction(16, 3))
        self.assertEqual(rebuilt["laplacian"], Fraction(8, 3))
        self.assertEqual(rebuilt["q"], Fraction(-128, 9))
        self.assertEqual(producer["q_0"]["numerator"], -128)

    def test_weak_endpoint(self) -> None:
        self.assertEqual(weak_endpoint_quotient(), Fraction(32, 17))
        self.assertEqual(reconstruct_weak_quotient(), Fraction(32, 17))


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

    def test_mutation_fixture(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["zero_endpoint"]["nonzero_fixture"]["q_0"].__setitem__(
                "numerator", -127
            )
        )

    def test_mutation_endpoint_status(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["zero_endpoint"].__setitem__("status", "OPEN")
        )

    def test_mutation_constant_status(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["compactness_conclusion"].__setitem__(
                "constant_status", "COMPUTED"
            )
        )

    def test_mutation_global_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "positive_all_field_deterministic_gradient_bound", "PROVED"
            )
        )

    def test_mutation_witten_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "volume_uniform_witten_coercivity", "PROVED"
            )
        )

    def test_mutation_dependency_tag(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["dependency_tags"].__setitem__(
                2, "LORENTZIAN-CAUSAL"
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
