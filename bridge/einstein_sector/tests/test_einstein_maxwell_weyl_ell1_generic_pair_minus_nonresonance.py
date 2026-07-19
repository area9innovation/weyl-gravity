from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class Ell1GenericPairMinusNonresonanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_ell1_generic_pair_minus_nonresonance.json").read_text())

    def test_integer_reduction(self) -> None:
        self.assertEqual(self.value["integer_offset_reduction"]["angular_integer"], "D=L-ell belongs to {-1,0,1}")

    def test_exceptional_intervals(self) -> None:
        audit = self.value["interval_audit"]
        self.assertIn("only D=1", audit["exceptional_sum"]["minus"])
        self.assertIn("only D=-1", audit["exceptional_difference"]["minus"])

    def test_physical_intervals(self) -> None:
        audit = self.value["interval_audit"]
        self.assertIn("D>17/10", audit["physical_sum"])
        self.assertIn("(-4/5,-1/4)", audit["physical_difference"]["plus"])

    def test_complete_pair_census(self) -> None:
        self.assertTrue(self.value["classification"]["complete_k0_oscillator_pair_to_minus_census_closed"])

    def test_source_claim_is_fail_closed(self) -> None:
        self.assertFalse(self.value["classification"]["quadratic_source_coefficients_computed"])


if __name__ == "__main__":
    unittest.main()
