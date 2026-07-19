from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_axial_ell1_zero_source_fixture.json"


class ExceptionalAxialZeroSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_direct_rows(self) -> None:
        self.assertEqual(self.value["homogeneous_source_rows_E00_E11_E22_Maxwell1"], ["-16/9", "0", "-8/9", "0"])

    def test_normalization_is_explicit(self) -> None:
        self.assertIn("norm 1/3", self.value["axisymmetric_harmonic"])

    def test_fail_closed(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["all_m_promoted"])
        self.assertFalse(flags["combined_balanced_source_solved"])
        self.assertFalse(flags["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
