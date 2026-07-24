"""Mutation tests for the local commutant and spectral-C certificate."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify_document


HERE = Path(__file__).resolve().parent


class LocalCommutantSpectralCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def mutated(self) -> dict:
        return copy.deepcopy(self.data)

    def test_certificate(self) -> None:
        verify_document(self.data)

    def test_local_extra_involution_promotion_rejected(self) -> None:
        data = self.mutated()
        data["claim_flags"]["only_plus_minus_identity_local_involutions"] = False
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_canonical_spectral_c_promotion_rejected(self) -> None:
        data = self.mutated()
        data["claim_flags"]["spectral_c_canonical"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_unweighted_threshold_promotion_rejected(self) -> None:
        data = self.mutated()
        data["claim_flags"]["whole_half_axis_unweighted_norm_equivalence"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_scattering_hypothesis_deletion_rejected(self) -> None:
        data = self.mutated()
        data["scattering_c_equivalence"]["required_hypotheses"].pop()
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_import_hash_mutation_rejected(self) -> None:
        data = self.mutated()
        data["imports"]["incoming_witt_decomposition"]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            verify_document(data)


if __name__ == "__main__":
    unittest.main()
