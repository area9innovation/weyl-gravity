"""Tests for the BT corrector-slab amplitude-band certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_corrector_slab_amplitude_band_suppression import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_corrector_slab_amplitude_band_suppression import verify


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

    def test_rejects_positive_bin_digest_mutation(self) -> None:
        self.reject(lambda data: data["amplitude_interval_certificate"]["positive_band_partition"].__setitem__("bin_summary_sha256", "0" * 64))

    def test_rejects_inverse_bin_coefficient_mutation(self) -> None:
        self.reject(lambda data: data["amplitude_interval_certificate"]["inverse_band_partition"]["minimum_bin"]["constant_floor"].__setitem__("denominator", 1))

    def test_rejects_uniform_gap_mutation(self) -> None:
        self.reject(lambda data: data["amplitude_interval_certificate"]["uniform_residual_square_gap"].__setitem__("numerator", 2))

    def test_rejects_net_size_mutation(self) -> None:
        self.reject(lambda data: data["continuum_amplitude_union"].__setitem__("net_size", 801))

    def test_rejects_probability_exponent_mutation(self) -> None:
        self.reject(lambda data: data["continuum_amplitude_union"]["lambda_point_four_exponent"].__setitem__("denominator", 32))

    def test_rejects_all_amplitudes_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("all_amplitudes_beyond_the_certified_octave", "PROVED"))

    def test_rejects_global_corrector_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("all_large_corrector_backgrounds_contain_scaled_slab_tubes", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.reject(lambda data: data["method_disposition"].__setitem__("actual_interacting_H_minus_one_second_moment", "PROVED"))

    def test_rejects_dependency_promotion(self) -> None:
        self.reject(lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_rejects_input_hash_mutation(self) -> None:
        self.reject(lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64))


if __name__ == "__main__":
    unittest.main()
