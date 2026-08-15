"""Tests for the exact BT complete-g4 subpower pair-bound certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_subpower_pair_bounds_decision import (
    CERT_PATH,
    build,
)
from reverse_physics.verify_bt_euclidean_complete_g4_subpower_pair_bounds import (
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

    def test_rejects_pair_coefficient_mutation(self) -> None:
        self.reject(
            lambda data: data["pair_bounds"][0]["upstream"][
                "paired_coefficient"
            ].__setitem__("numerator", 323)
        )

    def test_rejects_representative_mutation(self) -> None:
        self.reject(
            lambda data: data["pair_bounds"][1]["upstream"]["representative"][
                "kernels"
            ][0]["arguments"][0].__setitem__(0, -2)
        )

    def test_rejects_raw_bound_constant_mutation(self) -> None:
        self.reject(
            lambda data: data["pair_bounds"][0].__setitem__(
                "raw_bound", "abs(I_1(L))<=63*omega(p)^2*G2(L)^2/N"
            )
        )

    def test_rejects_shifted_convolution_constant_mutation(self) -> None:
        self.reject(
            lambda data: data["convolution_bounds"].__setitem__(
                "J_bound", "J_L<=N*[1+log(R)]"
            )
        )

    def test_rejects_subpower_pair_set_mutation(self) -> None:
        self.reject(
            lambda data: data["power_sector_reduction"]["subpower_pairs"].append(3)
        )

    def test_rejects_pair_three_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "pair_3_scale", "O_LOG_SQUARED"
            )
        )

    def test_rejects_combined_power_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__(
                "combined_pairs_3_4_6_7_power_coefficient", "NEGATIVE"
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
