"""Tests for the BT corrector-slab cylinder-suppression certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_corrector_slab_cylinder_suppression import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_corrector_slab_cylinder_suppression import verify


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

    def test_rejects_robust_coefficient_mutation(self) -> None:
        self.reject(lambda data: data["robust_interval_certificate"]["coefficient_ledger"][0]["lower"].__setitem__("numerator", 0))

    def test_rejects_gap_mutation(self) -> None:
        self.reject(lambda data: data["robust_interval_certificate"]["residual_square_gap"].__setitem__("numerator", 1))

    def test_rejects_action_coefficient_mutation(self) -> None:
        self.reject(lambda data: data["gibbs_cylinder_probability"]["action_gap_coefficient"].__setitem__("denominator", 8))

    def test_rejects_probability_exponent_mutation(self) -> None:
        self.reject(lambda data: data["gibbs_cylinder_probability"]["lambda_point_four_exponent"].__setitem__("numerator", 2))

    def test_rejects_all_corrector_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("all_large_corrector_backgrounds_contain_certified_cylinders", "PROVED"))

    def test_rejects_hyperuniformity_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("Gibbs_corrector_hyperuniformity_bound", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
