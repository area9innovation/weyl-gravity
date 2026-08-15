"""Tests for the BT full-phase g6 current reconciliation certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_full_phase_g6_current_reconciliation import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_full_phase_g6_current_reconciliation import verify


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

    def test_rejects_action_derivative_mutation(self) -> None:
        self.reject(lambda data: data["exact_lattice_bridge_fixture"]["values"]["D_h_S2"].__setitem__("numerator", 5106))

    def test_rejects_current_flux_mutation(self) -> None:
        self.reject(lambda data: data["exact_lattice_bridge_fixture"]["values"]["flux_J3"].__setitem__("denominator", 7))

    def test_rejects_vector_normalization_mutation(self) -> None:
        self.reject(lambda data: data["complete_full_phase_M4"]["exact_vector_fixture"]["z2"].__setitem__("numerator", 5))

    def test_rejects_vector_formula_mutation(self) -> None:
        self.reject(lambda data: data["complete_full_phase_M4"]["exact_vector_fixture"]["M4_direct"].__setitem__("numerator", 25))

    def test_rejects_order_map_mutation(self) -> None:
        self.reject(lambda data: data["coupling_order_dictionary"].__setitem__("variance_order_map", "[g^6] equals M6"))

    def test_rejects_formula_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("complete_full_phase_M4_finite_volume_value", "NEGATIVE"))

    def test_rejects_large_volume_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("complete_full_phase_M4_large_volume_scaling", "PROVED"))

    def test_rejects_scope_transfer(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("one_cosine_M4_sign_transfer_to_full_phase", "ALLOWED"))

    def test_rejects_susceptibility_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("nonperturbative_background_current_susceptibility", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
