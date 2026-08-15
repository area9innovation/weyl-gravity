"""Tests for the BT all-large-amplitude slab suppression certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_corrector_slab_all_amplitude_suppression import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_corrector_slab_all_amplitude_suppression import verify


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

    def test_rejects_middle_bin_mutation(self) -> None:
        self.reject(lambda data: data["middle_octave_certificate"]["positive_bins"][0]["residual_square_gap"].__setitem__("numerator", 1))

    def test_rejects_middle_gap_mutation(self) -> None:
        self.reject(lambda data: data["middle_octave_certificate"]["uniform_residual_square_gap"].__setitem__("denominator", 1))

    def test_rejects_symbolic_branch_digest_mutation(self) -> None:
        self.reject(lambda data: data["asymptotic_octave_certificate"].__setitem__("symbolic_interval_branch_ledger_sha256", "0" * 64))

    def test_rejects_positive_gap_polynomial_mutation(self) -> None:
        self.reject(lambda data: data["asymptotic_octave_certificate"]["positive_orientation"]["gap_numerator_for_nine_tenths_B4"]["shifted_coefficients"][0].__setitem__("numerator", 0))

    def test_rejects_inverse_discarded_digest_mutation(self) -> None:
        self.reject(lambda data: data["asymptotic_octave_certificate"]["inverse_orientation"].__setitem__("discarded_ledger_sha256", "f" * 64))

    def test_rejects_outer_exponent_mutation(self) -> None:
        self.reject(lambda data: data["all_amplitude_union"]["lambda_point_four_outer_first_exponent"].__setitem__("numerator", 2879))

    def test_rejects_total_prefactor_mutation(self) -> None:
        self.reject(lambda data: data["all_amplitude_union"].__setitem__("total_prefactor", 3207))

    def test_rejects_morphology_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("arbitrary_large_corrector_has_slab_morphology", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
