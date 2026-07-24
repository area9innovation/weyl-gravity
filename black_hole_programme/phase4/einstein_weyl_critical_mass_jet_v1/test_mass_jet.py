"""Mutation tests for the critical Einstein--Weyl mass-jet certificate."""

from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify_document


HERE = Path(__file__).resolve().parent


class CriticalMassJetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "certificate.json").read_text())

    def mutated(self) -> dict:
        return copy.deepcopy(self.data)

    def test_certificate(self) -> None:
        verify_document(self.data)

    def test_crosswalk_promotion_rejected(self) -> None:
        data = self.mutated()
        data["claim_flags"]["physical_mass_jet_equals_intrinsic_radial_tau"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_qnm_slope_promotion_rejected(self) -> None:
        data = self.mutated()
        data["claim_flags"]["physical_massive_qnm_slope_certified"] = True
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_coulomb_derivative_mutation_rejected(self) -> None:
        data = self.mutated()
        data["endpoint_phase"]["coulomb_values"]["partial_mass_x_at_zero"] = "1/omega"
        with self.assertRaises(AssertionError):
            verify_document(data)

    def test_import_hash_mutation_rejected(self) -> None:
        data = self.mutated()
        data["imports"]["intrinsic_radial_partial_jet"]["sha256"] = "0" * 64
        with self.assertRaises(AssertionError):
            verify_document(data)


if __name__ == "__main__":
    unittest.main()
