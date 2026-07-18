"""Tests for the exceptional ell=1 current/Taub theorem."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_current_taub import DEFAULT_OUTPUT


class ExceptionalEll1CurrentTaubTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_current_gram(self) -> None:
        theorem = self.payload["current_theorem"]
        self.assertEqual(theorem["normalized_extra_Hermitian_current_Gram"], [["16", "0"], ["0", "3"]])
        self.assertEqual(theorem["extra_positive_frequency_inertia"], [2, 0])

    def test_pure_extra_obstructed(self) -> None:
        self.assertTrue(self.payload["classification"]["pure_exceptional_ell1_nonzero_tangents_second_order_obstructed"])

    def test_physical_modes_do_not_balance_extra(self) -> None:
        self.assertTrue(self.payload["classification"]["isolated_physical_plus_exceptional_ell1_common_zero_is_origin"])

    def test_mixed_opposite_sign_gate_open(self) -> None:
        self.assertFalse(self.payload["classification"]["mixed_balance_with_opposite_sign_sector_classified"])


if __name__ == "__main__":
    unittest.main()
