"""Tests for the BT complete-g4 seven-kernel reduction certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_seven_kernel_decision import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_complete_g4_seven_kernel_reduction import (
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

    def test_rejects_pair_partition_mutation(self) -> None:
        self.reject(
            lambda data: data["inversion_reduction"]["pairs"][0][
                "atlas_row_indices_one_based"
            ].__setitem__(1, 5)
        )

    def test_rejects_representative_flow_mutation(self) -> None:
        self.reject(
            lambda data: data["inversion_reduction"]["pairs"][0][
                "representative"
            ]["kernels"][0]["arguments"][0].__setitem__(0, -2)
        )

    def test_rejects_quartic_bound_mutation(self) -> None:
        self.reject(
            lambda data: data["paired_quartic_theorem"].__setitem__(
                "two_sided_bound", "0<=K4"
            )
        )

    def test_rejects_carrier_bound_mutation(self) -> None:
        self.reject(
            lambda data: data["negative_nested_carrier"].__setitem__(
                "exact_bound", "T_L<=0"
            )
        )

    def test_rejects_combined_kernel_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "combined_seven_kernel_large_volume_sign_and_scaling", "PROVED"
            )
        )

    def test_rejects_complete_M4_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "complete_M4_large_volume_sign_and_scaling", "DIVERGES"
            )
        )

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "DIVERGES"
            )
        )

    def test_rejects_dependency_tag_mutation(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("continuum_obstruction", True))


if __name__ == "__main__":
    unittest.main()
