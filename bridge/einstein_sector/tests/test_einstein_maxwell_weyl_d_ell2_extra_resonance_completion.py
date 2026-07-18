from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_d_ell2_extra_resonance_completion.json"


class DResonanceCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_both_parities_are_invertible(self) -> None:
        self.assertTrue(self.value["classification"]["d_cross_adjoint_map_invertible_in_both_parities"])
        self.assertEqual(self.value["parity_completion"]["block_diagonal_axial_polar_determinant"], "8266752")

    def test_full_extension_remains_open(self) -> None:
        self.assertFalse(self.value["classification"]["simultaneous_stabilizer_zero_locus_solved"])
        self.assertFalse(self.value["classification"]["full_second_order_equation_solved"])


if __name__ == "__main__":
    unittest.main()
