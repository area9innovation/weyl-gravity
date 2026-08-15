"""Tests for the BT inhomogeneous-twist gauge obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_inhomogeneous_twist_gauge_obstruction import (
    CERT_PATH,
    build,
    cycle_fixture,
)
from reverse_physics.verify_bt_euclidean_inhomogeneous_twist_gauge_obstruction import (
    independent_cycle_fixture,
    verify,
)


class ExactGaugeTests(unittest.TestCase):
    def test_gradient_twist_equals_field_translation(self) -> None:
        produced = cycle_fixture()
        independent = independent_cycle_fixture()
        self.assertEqual(
            tuple(produced["twisted_residual"]), independent["direct"]
        )
        self.assertEqual(independent["holonomy"], 1)
        self.assertEqual(independent["action"], Fraction(153, 16))


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

    def test_mutation_action_identity(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["gauge_covariance_theorem"].__setitem__("action_identity", "false")
        )

    def test_mutation_holonomy(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["exact_cycle_four_fixture"]["gradient_holonomy"].__setitem__("numerator", 2)
        )

    def test_mutation_longitudinal_response(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["route_disposition"].__setitem__("longitudinal_inhomogeneous_twist_response", "POSITIVE")
        )

    def test_mutation_scalar_transfer(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["route_disposition"].__setitem__("twist_response_to_scalar_witten_coercivity", "PROVED")
        )

    def test_mutation_source_route(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["route_disposition"].__setitem__("source_generating_functional_covariance", "OBSTRUCTED")
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["route_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "BOUNDED")
        )

    def test_mutation_extra_claim(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("lorentzian_transfer", "PROVED")
        )


if __name__ == "__main__":
    unittest.main()
