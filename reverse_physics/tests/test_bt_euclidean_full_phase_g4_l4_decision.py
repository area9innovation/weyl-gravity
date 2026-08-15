"""Tests for the exact full-phase BT L=4 M4 decision."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_full_phase_g4_l4_decision import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_full_phase_g4_l4_decision import verify


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.payload = json.load(handle)

    def test_builder_is_deterministic(self) -> None:
        self.assertEqual(self.payload, build())

    def test_independent_modular_verifier_accepts_certificate(self) -> None:
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

    def test_rejects_M4_mutation(self) -> None:
        self.reject(lambda data: data["exact_L4_decision"]["M4_full"].__setitem__("numerator", -2569186115493258))

    def test_rejects_term_mutation(self) -> None:
        self.reject(lambda data: data["exact_L4_decision"]["terms"][0]["value"].__setitem__("numerator", 55147376933566))

    def test_rejects_residue_mutation(self) -> None:
        self.reject(lambda data: data["exact_L4_decision"]["terms"][2]["modular_residues"].__setitem__(0, 0))

    def test_rejects_covariance_sum_mutation(self) -> None:
        self.reject(lambda data: data["independent_modular_verification"]["allowed_covariance_absolute_sum"].__setitem__("numerator", 2100640))

    def test_rejects_expression_bound_mutation(self) -> None:
        self.reject(lambda data: data["independent_modular_verification"]["expression_absolute_bound"].__setitem__("numerator", 1))

    def test_rejects_uniqueness_mutation(self) -> None:
        self.reject(lambda data: data["independent_modular_verification"].__setitem__("uniqueness_inequality", False))

    def test_rejects_large_volume_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("large_volume_full_phase_M4_sign_and_scaling", "NEGATIVE"))

    def test_rejects_remainder_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("uniform_perturbative_remainder", "PROVED"))

    def test_rejects_susceptibility_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("nonperturbative_background_current_susceptibility", "DIVERGENT"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "DIVERGENT"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
