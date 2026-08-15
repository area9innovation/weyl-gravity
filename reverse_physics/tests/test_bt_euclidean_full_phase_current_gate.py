"""Tests for the BT full-phase current gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_full_phase_current_gate import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_full_phase_current_gate import verify


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

    def test_rejects_current_mutation(self) -> None:
        self.reject(lambda data: data["exact_current_fixture"]["full_current_zero_mode"].__setitem__("numerator", 0))

    def test_rejects_current_identity_mutation(self) -> None:
        self.reject(lambda data: data["current_identity"].__setitem__("action_gradient", "unspecified"))

    def test_rejects_pair_constant_mutation(self) -> None:
        self.reject(lambda data: data["full_phase_reduction"].__setitem__("resulting_pair_moment", "unspecified"))

    def test_rejects_current_gate_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("translation_invariant_current_susceptibility_bound", "PROVED"))

    def test_rejects_second_factor_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("pointwise_second_factor_from_canonical_current_gradient", "PROVED"))

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_lorentzian_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))


if __name__ == "__main__":
    unittest.main()
