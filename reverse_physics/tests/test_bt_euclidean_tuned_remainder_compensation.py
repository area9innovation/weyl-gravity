"""Tests for the BT tuned remainder-compensation theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_tuned_remainder_compensation import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_tuned_remainder_compensation import verify


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

    def test_rejects_gap_mutation(self) -> None:
        self.reject(lambda data: data["coefficient_gap"]["gap"].__setitem__("numerator", 1))

    def test_rejects_M3_mutation(self) -> None:
        self.reject(lambda data: data["exact_parity"].__setitem__("cubic_norm_coefficient", "M3!=0"))

    def test_rejects_balance_mutation(self) -> None:
        self.reject(lambda data: data["exact_balance"].__setitem__("status", "OPEN"))

    def test_rejects_interacting_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("sign_or_scaling_of_exact_interacting_score", "DIVERGENT"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))


if __name__ == "__main__":
    unittest.main()
