"""Tests for the BT finite-volume uniform-twist response gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_twist_response_gate import (
    CERT_PATH,
    build,
    exact_twist_fixture,
)
from reverse_physics.verify_bt_euclidean_twist_response_gate import (
    independent_fixture,
    verify,
)


class ExactTwistTests(unittest.TestCase):
    def test_twist_curvature_matches_expected_hessian_fixture(self) -> None:
        produced = exact_twist_fixture()
        currents, densities, average = independent_fixture()
        self.assertEqual(produced["currents"], currents)
        self.assertEqual(produced["curvature_densities"], densities)
        self.assertEqual(average, Fraction(3, 2))


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

    def test_mutation_fixture_curvature(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_fixture"]["axis_average_curvature"].__setitem__("numerator", 2)
        )

    def test_mutation_response_identity(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_uniform_twist_identity"].__setitem__("response", "lambda^2*f''=alpha")
        )

    def test_mutation_observed_sign(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["finite_volume_diagnostic"]["summaries"][0].__setitem__("scaled_twist_response", -1.0)
        )

    def test_mutation_nontransfer_scope(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["witten_nontransfer_obstruction"].__setitem__("scope", "BT counterexample")
        )

    def test_mutation_thermodynamic_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__("positive_thermodynamic_twist_modulus", "PROVED")
        )

    def test_mutation_witten_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__("response_to_witten_coercivity_transfer", "PROVED")
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "BOUNDED")
        )

    def test_mutation_extra_claim(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("lorentzian_transfer", "PROVED")
        )


if __name__ == "__main__":
    unittest.main()
