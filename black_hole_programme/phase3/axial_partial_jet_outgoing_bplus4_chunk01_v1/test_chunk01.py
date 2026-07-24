"""Mutation tests for content-addressed Bplus4 chunk 01."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class Chunk01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_verifies(self) -> None:
        verify(copy.deepcopy(self.document))

    def test_rejects_content_address_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["adaptive_chunk"]["source_content_addressed"] = False
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_boundary_gate_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["boundary_gate"]["interval_difference_contains_zero"] = False
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_r4_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["full_Bplus4_at_r4_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_tplus_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["T_plus_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)


if __name__ == "__main__":
    unittest.main()
