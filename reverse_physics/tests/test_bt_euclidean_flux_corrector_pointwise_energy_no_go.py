"""Tests for the BT flux-corrector pointwise-energy no-go."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_flux_corrector_pointwise_energy_no_go import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_flux_corrector_pointwise_energy_no_go import verify


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

    def test_rejects_slab_mutation(self) -> None:
        self.reject(lambda data: data["localized_slab_family"]["exponent_matrix_time_by_space"][1].__setitem__(0, 1))

    def test_rejects_action_ratio_mutation(self) -> None:
        self.reject(lambda data: data["diverging_ratios"]["action_ratio_linear_coefficient"].__setitem__("numerator", 48))

    def test_rejects_energy_ratio_mutation(self) -> None:
        self.reject(lambda data: data["diverging_ratios"]["dirichlet_ratio_linear_coefficient"].__setitem__("denominator", 1))

    def test_rejects_action_no_go_weakening(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("pointwise_corrector_bound_by_N_omega_action", "OPEN"))

    def test_rejects_Gibbs_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("Gibbs_corrector_hyperuniformity_bound", "PROVED"))

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
