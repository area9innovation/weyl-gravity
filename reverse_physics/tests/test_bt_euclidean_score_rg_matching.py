"""Tests for the BT score/RG matching certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_score_rg_matching import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_score_rg_matching import verify


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
        mutation(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_rejects_residue_mutation(self) -> None:
        self.reject(
            lambda data: data["lattice_log_residue"]["residue_coefficient_over_pi_squared"].__setitem__("numerator", 6)
        )

    def test_rejects_matched_limit_mutation(self) -> None:
        self.reject(
            lambda data: data["matched_refinement"]["score_limit_exact"].__setitem__("numerator", 2)
        )

    def test_rejects_scale_conflation(self) -> None:
        self.reject(
            lambda data: data["scale_setting_split"].__setitem__("status", "SAME_LIMIT")
        )

    def test_rejects_zero_fiber_ward_transfer(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__("ordinary_eom_to_zero_fiber_score_transfer", "PROVED")
        )

    def test_rejects_nonperturbative_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__("nonperturbative_annealed_zero_fiber_score_bound", "PROVED")
        )

    def test_rejects_continuum_promotion(self) -> None:
        self.reject(
            lambda data: data["method_disposition"].__setitem__("continuum_limit", "ESTABLISHED")
        )

    def test_rejects_extra_field(self) -> None:
        self.reject(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
