"""Tests for the BT corrector-slab fiber-stability certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_corrector_slab_fiber_stability import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_corrector_slab_fiber_stability import verify


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

    def test_rejects_row_vector_mutation(self) -> None:
        self.reject(lambda data: data["row_cone_coercivity"]["row_one"]["base"][0].__setitem__("numerator", -2))

    def test_rejects_fiber_coefficient_mutation(self) -> None:
        self.reject(lambda data: data["fiber_action_lower_bound"]["coefficient"].__setitem__("numerator", 2682))

    def test_rejects_density_exponent_mutation(self) -> None:
        self.reject(lambda data: data["integrated_background_density"]["lambda_point_four_action_exponent"].__setitem__("denominator", 127))

    def test_rejects_point_probability_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("localized_slab_neighborhood_probability_bound", "PROVED"))

    def test_rejects_all_backgrounds_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("all_large_corrector_backgrounds_fiber_stable", "PROVED"))

    def test_rejects_Gibbs_corrector_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("Gibbs_corrector_hyperuniformity_bound", "PROVED"))

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
