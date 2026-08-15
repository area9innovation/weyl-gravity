"""Tests for the BT logarithmic-bubble entropy/soft-score balance."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_log_bubble_entropy_soft_score_balance import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_log_bubble_entropy_soft_score_balance import (
    verify,
)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.payload = json.load(handle)

    def test_builder_is_deterministic(self) -> None:
        self.assertEqual(self.payload, build())

    def test_independent_verifier_accepts_certificate(self) -> None:
        self.assertTrue(verify())


class MutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.payload = json.load(handle)

    def reject(self, mutation) -> None:
        changed = copy.deepcopy(self.payload)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        try:
            mutation(changed)
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_rejects_wall_action_mutation(self) -> None:
        self.reject(
            lambda data: data["optimized_wall"]["reduced_action"].__setitem__(
                "numerator", 1
            )
        )

    def test_rejects_entropy_gap_mutation(self) -> None:
        self.reject(
            lambda data: data["tuned_entropy_balance"]["positive_entropy_gap"].__setitem__(
                "numerator", -1
            )
        )

    def test_rejects_linear_soft_factor(self) -> None:
        self.reject(
            lambda data: data["soft_score_balance"].__setitem__(
                "discrete_transfer", "|D_h A_L|=O(K/L)"
            )
        )

    def test_rejects_actual_score_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "actual_annealed_zero_fiber_score_bound", "PROVED"
            )
        )

    def test_rejects_cluster_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "interacting_multibubble_cluster_bound", "PROVED"
            )
        )

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_H_minus_one_second_moment", "PROVED"
            )
        )

    def test_rejects_lorentzian_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))


if __name__ == "__main__":
    unittest.main()
