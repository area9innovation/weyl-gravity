"""Mutation tests for the local/nonlocal positivity certificate."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify_document

HERE = Path(__file__).resolve().parent


class PositivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def mutate(self, key: str, value: bool) -> dict:
        data = copy.deepcopy(self.data)
        data["claim_flags"][key] = value
        return data

    def test_certificate(self) -> None:
        verify_document(self.data)

    def test_factorized_c_promotion_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            verify_document(self.mutate("channel_factorized_c_automatic", True))

    def test_mass_jost_promotion_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            verify_document(self.mutate("mass_bach_local_equality_implies_global_jost_derivative", True))

    def test_complex_classification_promotion_rejected(self) -> None:
        with self.assertRaises(AssertionError):
            verify_document(self.mutate("complete_complex_reducibility_classification", True))

    def test_import_hash_mutation_rejected(self) -> None:
        data = copy.deepcopy(self.data)
        data["imports"]["commutant_and_spectral_c"]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            verify_document(data)


if __name__ == "__main__":
    unittest.main()
