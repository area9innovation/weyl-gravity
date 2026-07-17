"""Tests for adjacent-input exceptional L=1 nonresonance."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_exceptional_L1_nonresonance import DEFAULT_OUTPUT, build_certificate


class ExceptionalL1NonresonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_complete_exceptional_root_set(self) -> None:
        self.assertEqual(self.payload["target_root_set"]["omega_squared"], ["0", "4/3", "4"])
        self.assertTrue(self.payload["classification"]["no_exceptional_L1_output_resonance"])

    def test_complete_cross_ell_spectral_gate(self) -> None:
        self.assertTrue(self.payload["classification"]["complete_unbounded_cross_ell_nonzero_output_nonresonance"])

    def test_source_remains_open(self) -> None:
        self.assertFalse(self.payload["classification"]["cross_ell_quadratic_source_solved"])


if __name__ == "__main__":
    unittest.main()
