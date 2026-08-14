"""Tests for the complete-g^4 Wiener-chaos gate reduction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_chaos_gate import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_complete_g4_chaos_gate import verify


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

    def test_rejects_hermite_norm_mutation(self) -> None:
        self.reject(
            lambda data: data["exact_hermite_fixture"]["values"]["norm_D_squared"].__setitem__(
                "numerator", 3057
            )
        )

    def test_rejects_cross_projection_mutation(self) -> None:
        self.reject(
            lambda data: data["exact_hermite_fixture"]["values"][
                "twice_A_Pi2E"
            ].__setitem__("numerator", 45)
        )

    def test_rejects_reduction_mutation(self) -> None:
        self.reject(
            lambda data: data["chaos_inventory"].__setitem__(
                "exact_reduction", "M4=||D||^2"
            )
        )

    def test_rejects_effective_kernel_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "effective_second_chaos_kernel_norm_bound", "PROVED"
            )
        )

    def test_rejects_whole_lattice_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "whole_lattice_order_g_four_power_survival", "PROVED"
            )
        )

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "DIVERGENT"
            )
        )

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
