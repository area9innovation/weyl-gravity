"""Tests for the BT exponential-action/current-spike certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_action_exponential_current_spike_gate import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_action_exponential_current_spike_gate import verify


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

    def test_rejects_affine_shift_mutation(self) -> None:
        self.reject(lambda data: data["actual_gibbs_exponential_moment"]["affine_shift"].__setitem__("numerator", 245))

    def test_rejects_theta_mutation(self) -> None:
        self.reject(lambda data: data["lambda_point_four_bulk_tail"]["theta"].__setitem__("denominator", 7))

    def test_rejects_tail_rate_mutation(self) -> None:
        self.reject(lambda data: data["lambda_point_four_bulk_tail"]["tail_rate"].__setitem__("numerator", 16))

    def test_rejects_motif_support_mutation(self) -> None:
        self.reject(lambda data: data["compact_slice_current_motif"]["exponent_support"][0].__setitem__("exponent", 1))

    def test_rejects_motif_action_mutation(self) -> None:
        self.reject(lambda data: data["compact_slice_current_motif"]["action"].__setitem__("numerator", 2084))

    def test_rejects_motif_current_mutation(self) -> None:
        self.reject(lambda data: data["compact_slice_current_motif"]["total_time_current"].__setitem__("numerator", 338))

    def test_rejects_coherence_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("moderate_current_phase_coherence", "PROVED"))

    def test_rejects_background_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("background_marginal_zero_fiber_action_tail", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
