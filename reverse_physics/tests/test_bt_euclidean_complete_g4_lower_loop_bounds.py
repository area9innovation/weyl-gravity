"""Tests for the BT complete-g4 lower-loop theorem."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_lower_loop_atlas import build as build_atlas
from reverse_physics.bt_euclidean_complete_g4_lower_loop_bounds import build as build_data
from reverse_physics.bt_euclidean_complete_g4_lower_loop_bounds_decision import CERT_PATH, build as build_certificate
from reverse_physics.verify_bt_euclidean_complete_g4_lower_loop_bounds import verify


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.payload = json.load(handle)

    def test_atlas_builder_is_deterministic(self) -> None:
        self.assertEqual(build_atlas()["checks"], {key: True for key in build_atlas()["checks"]})

    def test_data_builder_is_deterministic(self) -> None:
        result = build_data()
        self.assertTrue(all(result["checks"].values()))
        self.assertEqual(result["one_loop_summary"]["weight_sum_counts"], {"1": 4, "2": 15, "3": 8})

    def test_certificate_builder_is_deterministic(self) -> None:
        self.assertEqual(self.payload, build_certificate())

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

    def test_rejects_zero_loop_limit_mutation(self) -> None:
        self.reject(lambda data: data["zero_loop"].__setitem__("large_volume_limit", "0"))

    def test_rejects_one_loop_status_mutation(self) -> None:
        self.reject(lambda data: data["one_loop_summary"].__setitem__("asymptotic_status", "O_L"))

    def test_rejects_common_multiplier_mutation(self) -> None:
        self.reject(lambda data: data["one_loop_summary"]["common_bound_multiplier"].__setitem__("numerator", 1))

    def test_rejects_complete_sign_mutation(self) -> None:
        self.reject(lambda data: data["complete_leading_power"].__setitem__("status", "OPEN"))

    def test_rejects_interacting_promotion(self) -> None:
        self.reject(lambda data: data.__setitem__("interacting_H_minus_one", "DIVERGES"))

    def test_rejects_dependency_tag_mutation(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))


if __name__ == "__main__":
    unittest.main()
