"""Tests for the BT complete-g^4 connected-normalization certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_complete_g4_connected_normalization import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_complete_g4_connected_normalization import verify


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

    def test_rejects_H_mean_mutation(self) -> None:
        self.reject(lambda data: data["exact_gaussian_fixture"]["values"]["mean_H"].__setitem__("numerator", -24))

    def test_rejects_connected_identity_mutation(self) -> None:
        self.reject(lambda data: data["exact_gaussian_fixture"]["values"]["M4_connected"].__setitem__("numerator", 589))

    def test_rejects_cancellation_mutation(self) -> None:
        self.reject(lambda data: data["exact_gaussian_fixture"]["values"]["disconnected_cross_contribution"].__setitem__("numerator", -24))

    def test_rejects_preflight_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("exact_whole_lattice_M4_cancellation", "PROVED"))

    def test_rejects_full_kernel_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("full_combined_Pi2E_norm_bound", "PROVED"))

    def test_rejects_power_survival_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("whole_lattice_order_g_four_power_survival", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "DIVERGENT"))

    def test_rejects_conditioned_rank_audit_mutation(self) -> None:
        self.reject(lambda data: data["conditioned_rank_correction_audit"].__setitem__("maximum_viable_loop_rank", 3))

    def test_rejects_bulk_table_scope_mutation(self) -> None:
        self.reject(lambda data: data["connected_pairing_audit"].__setitem__("table_scope", "all conditioned contractions"))

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
