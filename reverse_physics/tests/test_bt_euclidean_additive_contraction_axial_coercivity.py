"""Tests for the BT additive contraction and axial coercivity theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_additive_contraction_axial_coercivity import (
    CERT_PATH,
    additive_fixture,
    axial_fixture,
    build,
    even_trig_average,
)
from reverse_physics.verify_bt_euclidean_additive_contraction_axial_coercivity import (
    exact_fourier_fixture,
    reconstruct_cycle_fixture,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_cycle_fixture_reconstruction(self) -> None:
        fixture = additive_fixture()
        rebuilt = reconstruct_cycle_fixture(fixture)
        self.assertEqual(rebuilt["later"], rebuilt["predicted"])
        self.assertGreater(rebuilt["initial_action"], rebuilt["later_action"])
        self.assertEqual(rebuilt["derivative"], -9)

    def test_exact_trigonometric_moments(self) -> None:
        self.assertEqual(even_trig_average(0, 1), Fraction(1, 2))
        self.assertEqual(even_trig_average(2, 0), Fraction(3, 8))
        self.assertEqual(even_trig_average(1, 1), Fraction(1, 8))
        self.assertEqual(even_trig_average(2, 1), Fraction(1, 16))

    def test_method_distinct_fourier_fixture(self) -> None:
        producer = axial_fixture()
        verifier = exact_fourier_fixture()
        self.assertEqual(
            verifier["residual_norm"],
            Fraction(
                producer["residual_norm_squared_average"]["numerator"],
                producer["residual_norm_squared_average"]["denominator"],
            ),
        )
        self.assertEqual(verifier["gradient_norm"], Fraction(17, 4))


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

    def test_mutation_flow_fixture(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["additive_positive_field_contraction"][
                "exact_fixture"
            ]["omega"][0].__setitem__("numerator", 2)
        )

    def test_mutation_axial_norm(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["continuum_axial_coercivity"]["exact_fixture"][
                "gradient_norm_squared_average"
            ].__setitem__("numerator", 1)
        )

    def test_mutation_ward_identity(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["reciprocal_field_ward_identity"].__setitem__(
                "identity", "unknown"
            )
        )

    def test_mutation_method_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "volume_uniform_witten_coercivity", "PROVED"
            )
        )

    def test_mutation_hodge_gate(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["multidimensional_hodge_gate"].__setitem__(
                "curl_identity", "unknown"
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
