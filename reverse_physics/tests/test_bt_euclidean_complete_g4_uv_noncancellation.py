"""Tests for complete-g^4 UV-local noncancellation."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_uv_noncancellation import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_complete_g4_uv_noncancellation import verify


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

    def test_rejects_action_coefficient_mutation(self) -> None:
        self.reject(
            lambda data: data["exact_action_expansion"]["exact_fixture"]["S3"].__setitem__(
                "numerator", 12
            )
        )

    def test_rejects_fiber_variance_mutation(self) -> None:
        self.reject(
            lambda data: data["free_fiber_effective_action"]["exact_fixture"][
                "VarS1"
            ].__setitem__("numerator", 2191)
        )

    def test_rejects_normalization_mutation(self) -> None:
        self.reject(
            lambda data: data["complete_order_g_four"]["exact_normalization_fixture"][
                "M4_direct"
            ].__setitem__("numerator", -210)
        )

    def test_rejects_incomplete_formula(self) -> None:
        self.reject(
            lambda data: data["complete_order_g_four"].__setitem__(
                "direct_formula", "M4=E0[B^2]"
            )
        )

    def test_rejects_whole_lattice_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "whole_lattice_order_g_four_power_cancellation", "OBSTRUCTED"
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
