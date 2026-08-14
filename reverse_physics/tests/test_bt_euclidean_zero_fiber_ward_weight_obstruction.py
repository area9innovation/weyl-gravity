"""Tests for the BT zero-fiber Ward-weight obstruction certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_zero_fiber_ward_weight_obstruction import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_zero_fiber_ward_weight_obstruction import verify


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

    def test_rejects_density_bound_mutation(self) -> None:
        self.reject(lambda data: data["bt_runaway_density_obstruction"].__setitem__("density_bound", "q_m^(u)(0)<=1"))

    def test_rejects_change_of_measure_mutation(self) -> None:
        self.reject(lambda data: data["constrained_measure_change"].__setitem__("radon_nikodym", "dmu_0/dnu=1"))

    def test_rejects_gaussian_target_mutation(self) -> None:
        self.reject(lambda data: data["shifted_gaussian_no_transfer"]["fixture"]["unweighted_score_second_moment"].__setitem__("numerator", 99))

    def test_rejects_pointwise_transfer_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("pointwise_constrained_ward_to_annealed_score_transfer", "PROVED"))

    def test_rejects_annealed_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("annealed_inverse_density_or_center_bound", "PROVED"))

    def test_rejects_continuum_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("continuum_limit", "ESTABLISHED"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
