from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_zero_frequency_source.json"


class ExceptionalEllipseZeroFrequencySourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_full_homogeneous_vector_cancels(self) -> None:
        self.assertEqual(self.value["homogeneous_zero_frequency_source"]["combined"], ["0", "0", "0", "0"])

    def test_every_other_zero_channel_is_invertible(self) -> None:
        self.assertTrue(self.value["classification"]["all_other_zero_frequency_outputs_invertible"])
        self.assertIn("homogeneous correction is zero", self.value["remaining_zero_frequency_channels"]["conclusion"])

    def test_mixed_ell_normalization_is_repaired(self) -> None:
        self.assertTrue(self.value["classification"]["mixed_ell_normalization_repaired"])
        self.assertIn("17496", self.value["direct_representative_amplitudes"]["Einstein_minus_axial"])

    def test_nonzero_frequency_gate_remains_open(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["complete_nonzero_frequency_polynomial_source_solved"])
        self.assertFalse(flags["bounded_second_order_extension_certified"])
        self.assertFalse(flags["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
