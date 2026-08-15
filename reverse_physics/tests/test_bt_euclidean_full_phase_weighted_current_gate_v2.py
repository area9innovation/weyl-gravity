"""Tests for the slice-valid BT weighted-current V2 gate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_full_phase_weighted_current_gate_v2 import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_full_phase_weighted_current_gate_v2 import verify


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

    def test_rejects_slice_projection_mutation(self) -> None:
        self.reject(lambda data: data["slice_valid_fixture"]["exponent_matrix_time_by_space"][0].__setitem__(0, 1))

    def test_rejects_slice_current_mutation(self) -> None:
        self.reject(lambda data: data["slice_valid_fixture"]["full_time_current_zero_mode"].__setitem__("numerator", 0))

    def test_rejects_weighted_identity_mutation(self) -> None:
        self.reject(lambda data: data["weighted_current_normal_form"].__setitem__("identity", "unspecified"))

    def test_rejects_corrector_split_mutation(self) -> None:
        self.reject(lambda data: data["plain_gradient_corrector_split"].__setitem__("decomposition", "unspecified"))

    def test_rejects_weighted_potential_bound_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("weighted_potential_mass_structure_factor_bound", "PROVED"))

    def test_rejects_v1_scope_repromotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("v1_fixture_as_full_phase_slice_witness", "PROVED"))

    def test_rejects_flux_corrector_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("translation_invariant_flux_corrector_bound", "PROVED"))

    def test_rejects_susceptibility_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("translation_invariant_current_susceptibility_bound", "PROVED"))

    def test_rejects_H_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_lorentzian_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))


if __name__ == "__main__":
    unittest.main()
