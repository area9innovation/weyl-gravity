"""Tests for the BT logarithmic-bubble homogeneous-virial no-go."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_log_bubble_virial_no_go import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_log_bubble_virial_no_go import verify


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

    def test_rejects_smoothstep_moment_mutation(self) -> None:
        self.reject(lambda data: data["exact_radial_integrals"]["smoothstep_integrals"]["integral_W_cubed"].__setitem__("numerator", 25))

    def test_rejects_reduced_virial_mutation(self) -> None:
        self.reject(lambda data: data["exact_radial_integrals"]["reduced_radial_virial"].__setitem__("numerator", 1))

    def test_rejects_transfer_status_mutation(self) -> None:
        self.reject(lambda data: data["finite_lattice_transfer"].__setitem__("status", "NUMERICAL_SEQUENCE"))

    def test_rejects_uniform_expansion_mutation(self) -> None:
        self.reject(lambda data: data["finite_lattice_transfer"]["uniform_expansions"].__setitem__(0, "r_L has an unspecified limit"))

    def test_rejects_gibbs_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("nonpointwise_Gibbs_weighted_block_estimate", "PROVED"))

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_lorentzian_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))


if __name__ == "__main__":
    unittest.main()
