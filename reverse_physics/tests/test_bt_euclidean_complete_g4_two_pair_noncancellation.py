"""Tests for BT complete-g4 two-pair noncancellation."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_two_pair_noncancellation_decision import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_complete_g4_two_pair_noncancellation import verify


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

    def test_rejects_dispersion_constant_mutation(self) -> None:
        self.reject(lambda data: data["dispersion_theorem"].__setitem__("claim", "norm(F)^2 <= 10*A*B*C"))

    def test_rejects_coarse_sum_mutation(self) -> None:
        self.reject(lambda data: data["pair_seven_bound"].__setitem__("coarse_inverse_integer_sum", 1))

    def test_rejects_centered_sum_mutation(self) -> None:
        self.reject(lambda data: data["pair_seven_bound"].__setitem__("coarse_centered_integer_sum", 1))

    def test_rejects_c7_interval_mutation(self) -> None:
        self.reject(lambda data: data["pair_seven_bound"]["c_7_upper"].__setitem__("numerator", 1))

    def test_rejects_combined_sign_mutation(self) -> None:
        self.reject(lambda data: data["comparison"].__setitem__("combined", "c_4+c_7=0"))

    def test_rejects_complete_M4_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("complete_M4_large_volume_sign_and_scaling", "NEGATIVE"))

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "DIVERGES"))

    def test_rejects_dependency_tag_mutation(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("continuum_limit_proved", True))


if __name__ == "__main__":
    unittest.main()
