"""Tests for the exceptional ell=1 twist-resonance no-go."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_twist_resonance import DEFAULT_OUTPUT


class ExceptionalEll1TwistResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_common_zero_fixture(self) -> None:
        self.assertEqual(self.payload["first_order_common_zero_fixture"]["balance"], "B^2=(8/3)*e^2")
        self.assertTrue(self.payload["classification"]["nonzero_twist_exceptional_common_zero_fixture_constructed"])

    def test_exact_resonance(self) -> None:
        theorem = self.payload["resonance_theorem"]
        self.assertEqual(theorem["output_frequency_squared"], "16/3")
        self.assertEqual(theorem["target_matrix_rank"], 2)
        self.assertEqual(theorem["augmented_matrix_rank"], 3)

    def test_nonzero_dual_witness(self) -> None:
        self.assertEqual(self.payload["resonance_theorem"]["adjoint_pairings"], ["-2/3", "4/3"])
        self.assertTrue(self.payload["classification"]["nonzero_adjoint_cokernel_witness_certified"])

    def test_second_order_no_go(self) -> None:
        self.assertFalse(self.payload["classification"]["twist_balanced_fixture_second_order_extendible"])


if __name__ == "__main__":
    unittest.main()
