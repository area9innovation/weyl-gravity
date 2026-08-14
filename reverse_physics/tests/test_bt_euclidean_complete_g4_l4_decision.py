"""Tests for the exact L=4 complete BT g^4 decision certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_l4_decision import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_complete_g4_l4_decision import verify


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

    def test_rejects_M4_mutation(self) -> None:
        self.reject(lambda data: data["exact_L4_decision"]["M4"].__setitem__("numerator", -338835474713436))

    def test_rejects_term_mutation(self) -> None:
        self.reject(lambda data: data["exact_L4_decision"]["term_ledger"][0]["value"].__setitem__("numerator", 1))

    def test_rejects_sector_mutation(self) -> None:
        self.reject(lambda data: data["exact_L4_decision"]["rank_loop_sector_totals"][2]["value"].__setitem__("numerator", 1))

    def test_rejects_bound_mutation(self) -> None:
        self.reject(lambda data: data["independent_modular_verification"].__setitem__("integer_difference_bound", 1))

    def test_rejects_modular_source_hash_mutation(self) -> None:
        self.reject(lambda data: data["independent_modular_verification"].__setitem__("source_sha256", "0" * 64))

    def test_rejects_asymptotic_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("large_volume_M4_sign_and_scaling", "NEGATIVE"))

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "DIVERGENT"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "continuum cancellation"))


if __name__ == "__main__":
    unittest.main()
