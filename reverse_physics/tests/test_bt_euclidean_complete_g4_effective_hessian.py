"""Tests for the complete-g^4 expected-Hessian certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_effective_hessian import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_complete_g4_effective_hessian import verify


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.payload = json.load(handle)

    def test_builder_is_deterministic(self) -> None:
        self.assertEqual(self.payload, build())

    def test_verifier_accepts_certificate(self) -> None:
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

    def test_rejects_expected_hessian_mutation(self) -> None:
        self.reject(lambda data: data["exact_one_dimensional_fixture"]["values"]["expected_hessian_direct"].__setitem__("numerator", 526))

    def test_rejects_norm_mutation(self) -> None:
        self.reject(lambda data: data["exact_one_dimensional_fixture"]["values"]["Pi2E_norm_squared"].__setitem__("denominator", 31))

    def test_rejects_kernel_status_mutation(self) -> None:
        self.reject(lambda data: data["combined_effective_hessian"].__setitem__("status", "OPEN"))

    def test_rejects_momentum_kernel_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("explicit_lattice_momentum_kernel", "PROVED"))

    def test_rejects_norm_bound_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("effective_second_chaos_kernel_norm_bound", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "DIVERGENT"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
