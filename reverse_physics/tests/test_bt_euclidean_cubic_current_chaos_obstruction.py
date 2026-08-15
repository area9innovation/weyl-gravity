"""Tests for the BT cubic-current chaos obstruction certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_cubic_current_chaos_obstruction import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_cubic_current_chaos_obstruction import verify


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

    def test_rejects_motif_mutation(self) -> None:
        self.reject(lambda data: data["compact_cubic_motif"]["exponent_support"][0].__setitem__("value", 1))

    def test_rejects_profile_mutation(self) -> None:
        self.reject(lambda data: data["compact_cubic_motif"]["cubic_current_row_profile"][0].__setitem__("numerator", 43))

    def test_rejects_norm_mutation(self) -> None:
        self.reject(lambda data: data["compact_cubic_motif"]["free_action_inner_product_norm_squared"].__setitem__("numerator", 349))

    def test_rejects_support_count_mutation(self) -> None:
        self.reject(lambda data: data["compact_cubic_motif"].__setitem__("nonzero_cubic_current_count", 44))

    def test_rejects_variance_density_mutation(self) -> None:
        self.reject(lambda data: data["extensive_variance_obstruction"]["general_variance_density"].__setitem__("numerator", 1082))

    def test_rejects_tuned_density_mutation(self) -> None:
        self.reject(lambda data: data["extensive_variance_obstruction"]["lambda_point_four_variance_density"].__setitem__("numerator", 69311))

    def test_rejects_divergence_mutation(self) -> None:
        self.reject(lambda data: data["extensive_variance_obstruction"]["normalized_divergence_coefficient"].__setitem__("numerator", 4331))

    def test_rejects_ward_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("cross_order_and_measure_Ward_cancellation", "PROVED"))

    def test_rejects_complete_perturbative_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("complete_perturbative_current_susceptibility", "OBSTRUCTED"))

    def test_rejects_interacting_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("nonperturbative_background_marginal_susceptibility", "OBSTRUCTED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
