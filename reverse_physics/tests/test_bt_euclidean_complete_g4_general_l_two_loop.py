"""Tests for the generic-L BT complete-g4 two-loop certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_general_l_two_loop_decision import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_complete_g4_general_l_two_loop import (
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

    def test_rejects_integrand_coefficient_mutation(self) -> None:
        self.reject(
            lambda data: data["two_loop_atlas"]["surviving_integrands"][0][
                "coefficient"
            ].__setitem__("numerator", 163)
        )

    def test_rejects_affine_flow_mutation(self) -> None:
        self.reject(
            lambda data: data["two_loop_atlas"]["surviving_integrands"][0][
                "kernels"
            ][0]["arguments"][0].__setitem__(0, -2)
        )

    def test_rejects_cancellation_count_mutation(self) -> None:
        self.reject(
            lambda data: data["two_loop_atlas"]["statistics"].__setitem__(
                "exactly_canceled_integrand_count", 4
            )
        )

    def test_rejects_factorized_formula_mutation(self) -> None:
        self.reject(
            lambda data: data["factorized_conditioning_sector"].__setitem__(
                "exact_formula", "R_L=0"
            )
        )

    def test_rejects_green_bound_mutation(self) -> None:
        self.reject(
            lambda data: data["factorized_conditioning_sector"].__setitem__(
                "four_dimensional_green_bound", "sum <= 0"
            )
        )

    def test_rejects_remaining_kernel_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "remaining_fourteen_unfactorized_two_loop_kernel_bound", "PROVED"
            )
        )

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "actual_interacting_h_minus_one_second_moment", "BOUNDED"
            )
        )

    def test_rejects_dependency_tag_mutation(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("large_volume_theorem", True))


if __name__ == "__main__":
    unittest.main()
