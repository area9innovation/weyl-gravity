"""Tests for the BT cubic-score logarithmic obstruction."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_cubic_score_log_obstruction import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_cubic_score_log_obstruction import verify


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
        mutation(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_rejects_vertex_mutation(self) -> None:
        self.reject(
            lambda data: data["exact_cubic_expansion"]["exact_fixture"]["vertex"].__setitem__("numerator", -15)
        )

    def test_rejects_lower_bound_mutation(self) -> None:
        self.reject(
            lambda data: data["rigorous_logarithmic_lower_bound"]["lower_bound_per_block"].__setitem__("denominator", 4_665_599)
        )

    def test_rejects_numerical_mutation(self) -> None:
        self.reject(
            lambda data: data["numerical_preflight"]["table"][0].__setitem__("coefficient_C_L", 0.0)
        )

    def test_rejects_nonperturbative_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__("nonperturbative_annealed_zero_fiber_score_bound", "PROVED")
        )

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "OBSTRUCTED")
        )

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
