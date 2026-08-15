"""Tests for the coordinate-correct BT electrical Witten bridge."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from fractions import Fraction

from reverse_physics.bt_euclidean_riemannian_electrical_witten_bridge import (
    CERT_PATH,
    build,
    cycle_fixture,
)
from reverse_physics.verify_bt_euclidean_riemannian_electrical_witten_bridge import (
    independent_fixture,
    verify,
)


class ExactBridgeTests(unittest.TestCase):
    def test_source_and_score_use_same_operator(self) -> None:
        produced = cycle_fixture()
        independent = independent_fixture()
        self.assertEqual(tuple(produced["source_covector"]), independent["alpha"])
        self.assertEqual(tuple(produced["score_vector"]), independent["score"])
        self.assertEqual(independent["electrical"], Fraction(9, 20))

    def test_metric_volume_and_source_norm(self) -> None:
        independent = independent_fixture()
        self.assertEqual(independent["relative_volume_squared"], Fraction(16, 15625))
        self.assertEqual(independent["norm"], 2)


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

    def test_mutation_conductance_operator(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["cycle_four_fixture"]["conductance_laplacian"][0][0].__setitem__(
                "numerator", 3
            )
        )

    def test_mutation_metric(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["cycle_four_fixture"]["riemannian_metric"][0][0].__setitem__(
                "numerator", 84
            )
        )

    def test_mutation_identity_metric_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "flat_potential_euclidean_dirichlet_substitution", "PROVED"
            )
        )

    def test_mutation_parallel_connection(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["parallel_source_witten_identity"].__setitem__(
                "operator_identity", "L_1(dF_h)=0"
            )
        )

    def test_mutation_witten_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "volume_uniform_annealed_witten_coercivity", "PROVED"
            )
        )

    def test_mutation_moment_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "BOUNDED"
            )
        )

    def test_mutation_extra_claim(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert.__setitem__("lorentzian_transfer", "PROVED")
        )


if __name__ == "__main__":
    unittest.main()
