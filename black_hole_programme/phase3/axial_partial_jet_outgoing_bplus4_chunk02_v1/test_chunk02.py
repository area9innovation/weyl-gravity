"""Mutation tests for Bplus4 successor chunk 02."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class Chunk02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_verifies(self) -> None:
        verify(copy.deepcopy(self.document))

    def test_rejects_primary_selection_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["adaptive_chunk"]["larger_primary_selected"] = False
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_direct_gate_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["boundary_gate"]["partial_jet_coefficients_equal_direct"] = False
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_r4_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["full_Bplus4_at_r4_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_stokes_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["stokes_or_scattering_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)


if __name__ == "__main__":
    unittest.main()
