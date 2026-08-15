"""Tests for the BT radial-convexity obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_radial_convexity_obstruction import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_radial_convexity_obstruction import verify


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

    def test_rejects_profile_mutation(self) -> None:
        self.reject(lambda data: data["exact_fixture"]["shell_exponents"].__setitem__(12, 213))

    def test_rejects_action_mutation(self) -> None:
        self.reject(lambda data: data["exact_fixture"]["action_A"].__setitem__("numerator", 1))

    def test_rejects_curvature_sign_mutation(self) -> None:
        self.reject(lambda data: data["exact_fixture"]["radial_curvature_log_squared_coefficient_C_2"].__setitem__("numerator", 1))

    def test_rejects_weaker_constant_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("pointwise_D_ge_cA_for_0_lt_c_lt_1", "PROVED"))

    def test_rejects_lorentzian_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))


if __name__ == "__main__":
    unittest.main()
