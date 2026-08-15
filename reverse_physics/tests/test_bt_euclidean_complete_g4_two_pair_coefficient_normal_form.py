"""Tests for the BT complete-g4 two-pair coefficient normal forms."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_two_pair_coefficient_normal_form_decision import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_complete_g4_two_pair_coefficient_normal_form import (
    verify,
)


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

    def test_rejects_A4_lower_mutation(self) -> None:
        self.reject(lambda data: data["pair_four"]["A_4_lower"].__setitem__("numerator", 1))

    def test_rejects_S4_lower_mutation(self) -> None:
        self.reject(lambda data: data["pair_four"]["S_4_cube_lower"].__setitem__("denominator", 1))

    def test_rejects_pair_four_gap_mutation(self) -> None:
        self.reject(lambda data: data["pair_four"]["magnitude_lower"].__setitem__("numerator", 1))

    def test_rejects_derivative_mutation(self) -> None:
        self.reject(lambda data: data["pair_seven"].__setitem__("collapsed_derivative", "D_4=0"))

    def test_rejects_noncancellation_promotion(self) -> None:
        self.reject(lambda data: data["comparison_gate"].__setitem__("noncancellation", "PROVED"))

    def test_rejects_combined_sign_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("combined_pair_4_pair_7_coefficient", "NEGATIVE"))

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
