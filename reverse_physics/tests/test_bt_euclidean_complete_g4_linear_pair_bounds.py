"""Tests for the exact BT complete-g4 pair-3/pair-6 bound certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_linear_pair_bounds_decision import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_complete_g4_linear_pair_bounds import (
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

    def test_rejects_pair_three_representative_mutation(self) -> None:
        self.reject(
            lambda data: data["pair_bounds"][0]["upstream"]["representative"][
                "kernels"
            ][0]["arguments"][0].__setitem__(0, -2)
        )

    def test_rejects_pair_six_coefficient_mutation(self) -> None:
        self.reject(
            lambda data: data["pair_bounds"][1]["upstream"][
                "paired_coefficient"
            ].__setitem__("numerator", 181)
        )

    def test_rejects_quintic_constant_mutation(self) -> None:
        self.reject(
            lambda data: data["vertex_bounds"]["constants"][
                "quintic_all_leg_product"
            ].__setitem__("numerator", 9)
        )

    def test_rejects_inner_convolution_mutation(self) -> None:
        self.reject(
            lambda data: data["torus_convolution"].__setitem__(
                "inner_bound", "C_33(x)<=40000/max(1,rho(x))^2"
            )
        )

    def test_rejects_pair_three_bound_mutation(self) -> None:
        self.reject(
            lambda data: data["pair_bounds"][0].__setitem__(
                "explicit_bound", "abs(I_3(L))<=L"
            )
        )

    def test_rejects_five_pair_set_mutation(self) -> None:
        self.reject(
            lambda data: data["power_sector_reduction"]["subpower_pairs"].append(7)
        )

    def test_rejects_pair_four_seven_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "combined_pairs_4_7_power_coefficient", "NEGATIVE"
            )
        )

    def test_rejects_tuned_uniformity_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "pairs_3_6_tuned_g_four_uniformity", "PROVED"
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
