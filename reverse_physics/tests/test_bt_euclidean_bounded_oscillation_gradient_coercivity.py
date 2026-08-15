"""Tests for the BT bounded-oscillation gradient theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_bounded_oscillation_gradient_coercivity import (
    CERT_PATH,
    build,
    exact_cycle_fixture,
)
from reverse_physics.verify_bt_euclidean_bounded_oscillation_gradient_coercivity import (
    decode,
    independently_reconstruct_cycle,
    verify,
)


class ExactMathematicsTests(unittest.TestCase):
    def test_directed_reconstruction_matches_edge_producer(self) -> None:
        fixture = exact_cycle_fixture()
        rebuilt = independently_reconstruct_cycle(fixture["omega"])
        self.assertEqual(rebuilt["residual"], [decode(x) for x in fixture["residual"]])
        self.assertEqual(rebuilt["gradient"], [decode(x) for x in fixture["gradient"]])

    def test_weighted_residual_constraint(self) -> None:
        rebuilt = independently_reconstruct_cycle(exact_cycle_fixture()["omega"])
        self.assertEqual(rebuilt["weighted_sum"], 0)

    def test_exact_bound_has_slack(self) -> None:
        rebuilt = independently_reconstruct_cycle(exact_cycle_fixture()["omega"])
        self.assertGreater(rebuilt["slack"], 0)

    def test_theorem_exponent_and_collapse_condition(self) -> None:
        certificate = build()
        self.assertIn("(m/M)^12", certificate["theorem"]["conclusion"])
        self.assertIn("->infinity", certificate["theorem"]["collapse_necessary_condition"])


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
            lambda cert: cert["exact_fixture"]["omega"][0].__setitem__("numerator", 2)
        )

    def test_mutation_theorem(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["theorem"].__setitem__(
                "conclusion", "||grad A||^2 >= omega_G^2 ||r||^2"
            )
        )

    def test_mutation_method_boundary(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "all_field_volume_uniform_gradient_bound", "PROVED"
            )
        )

    def test_mutation_extra_field(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert.__setitem__("claim", True))


if __name__ == "__main__":
    unittest.main()
