"""Tests for the BT quartic-score power-obstruction certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_quartic_score_power_obstruction import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_quartic_score_power_obstruction import verify


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

    def test_rejects_soft_derivative_mutation(self) -> None:
        self.reject(lambda data: data["exact_soft_fixture"]["epsilon_derivative"]["real"].__setitem__("numerator", -2))

    def test_rejects_power_bound_mutation(self) -> None:
        self.reject(lambda data: data["wiener_chaos_lower_bound"].__setitem__("normalized_bound", "bounded"))

    def test_rejects_complete_coefficient_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("complete_order_g_four_score_coefficient", "DIVERGENT"))

    def test_rejects_cancellation_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("power_cancellation_in_renormalized_zero_fiber_composite", "PROVED"))

    def test_rejects_interacting_divergence_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "DIVERGENT"))

    def test_rejects_continuum_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("continuum_limit", "ESTABLISHED"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
