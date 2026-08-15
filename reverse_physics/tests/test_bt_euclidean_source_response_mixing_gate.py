"""Focused tests for the BT source-response mixing gate."""

from __future__ import annotations

import copy
import json
import os
import unittest
from fractions import Fraction

from reverse_physics import bt_euclidean_source_response_experiment as experiment
from reverse_physics import bt_euclidean_source_response_mixing_gate as producer
from reverse_physics.verify_bt_euclidean_source_response_mixing_gate import verify


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SourceResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(producer.CERT_PATH, encoding="utf-8") as handle:
            cls.cert = json.load(handle)

    def assert_rejected(self, mutation) -> None:
        changed = copy.deepcopy(self.cert)
        mutation(changed)
        ok, _ = verify(changed)
        self.assertFalse(ok)

    def test_deterministic_builder(self) -> None:
        self.assertEqual(producer.build(), self.cert)

    def test_exact_mode_fixture(self) -> None:
        fixture = producer.exact_mode_fixture()
        self.assertEqual(fixture["full_lattice_delta_action"], Fraction(1372))
        self.assertEqual(
            fixture["proposed_residual"],
            [Fraction(9, 4), Fraction(-3, 2), Fraction(9, 4), Fraction(6)],
        )

    def test_independent_verifier(self) -> None:
        ok, checks = verify(self.cert)
        self.assertTrue(ok)
        self.assertEqual(sum(value for _, value in checks), 9)

    def test_smoke_experiment(self) -> None:
        data = experiment.experiment(smoke=True)
        self.assertEqual(len(data["runs"]), 2)
        self.assertEqual(
            [run["whole_mode_proposals_per_sweep"] for run in data["runs"]],
            [0, 1],
        )
        self.assertTrue(
            all(
                run["final_action_recompute_residual"] < 1.0e-8
                for run in data["runs"]
            )
        )

    def test_mutation_h_minus_one_promotion(self) -> None:
        self.assert_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "PROVED"
            )
        )

    def test_mutation_observation_promotion(self) -> None:
        self.assert_rejected(
            lambda cert: cert["method_disposition"].__setitem__(
                "mode_augmented_l6_l8_bilaplacian_scaling", "PROVED"
            )
        )

    def test_mutation_source_identity(self) -> None:
        self.assert_rejected(
            lambda cert: cert["source_response_identity"].__setitem__(
                "second_derivative", "D_J^2 log Z=0"
            )
        )

    def test_mutation_fixture(self) -> None:
        self.assert_rejected(
            lambda cert: cert["exact_cycle_four_tensor_fixture"].__setitem__(
                "full_4_to_the_4_delta_action",
                {"numerator": 1373, "denominator": 1},
            )
        )

    def test_mutation_mixing_disposition(self) -> None:
        self.assert_rejected(
            lambda cert: cert["numerical_preflight"].__setitem__(
                "disposition", "EQUILIBRATED"
            )
        )

    def test_mutation_extra_claim(self) -> None:
        self.assert_rejected(lambda cert: cert.__setitem__("continuum", "PROVED"))


if __name__ == "__main__":
    unittest.main()
