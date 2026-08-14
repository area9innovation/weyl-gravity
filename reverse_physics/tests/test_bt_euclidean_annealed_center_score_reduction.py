"""Tests for the BT annealed-center score reduction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_annealed_center_score_reduction import (
    CERT_PATH,
    build,
)
from reverse_physics.bt_euclidean_center_score_experiment import experiment
from reverse_physics.verify_bt_euclidean_annealed_center_score_reduction import (
    verify,
)


class ReductionTests(unittest.TestCase):
    def test_builder_is_deterministic(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.assertEqual(json.load(handle), build())

    def test_smoke_experiment_closes_numeric_center_inequality(self) -> None:
        payload = experiment(smoke=True)
        run = payload["runs"][0]
        self.assertLess(
            run["root_diagnostic"]["maximum_absolute_mode_score_residual"],
            1.0e-8,
        )
        self.assertLessEqual(
            run["root_diagnostic"]["maximum_center_score_inequality_residual"],
            1.0e-14,
        )


class MutationTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.payload = json.load(handle)

    def reject(self, mutation) -> None:
        changed = copy.deepcopy(self.payload)
        mutation(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_verifier_accepts_certificate(self) -> None:
        self.assertTrue(verify())

    def test_rejects_score_theorem_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "annealed_zero_fiber_score_bound", "PROVED"
            )
        )

    def test_rejects_integrated_moment_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "normalized_lowest_mode_second_moment", "PROVED"
            )
        )

    def test_rejects_gaussian_variance_mutation(self) -> None:
        self.reject(
            lambda data: data["logical_input_obstruction"]["exact_fixture"][
                "total_t_variance"
            ].__setitem__("numerator", 50)
        )

    def test_rejects_observation_hash_mutation(self) -> None:
        self.reject(
            lambda data: data["finite_volume_diagnostic"].__setitem__(
                "observation_sha256", "0" * 64
            )
        )

    def test_rejects_perturbative_promotion(self) -> None:
        self.reject(
            lambda data: data["perturbative_interface"].__setitem__(
                "claim_boundary", "NONPERTURBATIVE_THEOREM"
            )
        )

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
