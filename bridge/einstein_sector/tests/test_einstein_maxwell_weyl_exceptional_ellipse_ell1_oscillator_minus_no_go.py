from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class Ell1OscillatorMinusNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_ell1_oscillator_minus_no_go.json").read_text())

    def test_complete_ell1_inventory(self) -> None:
        inventory = self.value["ell1_sign_and_inventory"]
        self.assertEqual(inventory["exceptional_extra_frequency"], "2/sqrt(3)")
        self.assertEqual(inventory["physical_standard_frequency"], "2")

    def test_adjacent_gap_exclusion(self) -> None:
        exclusion = self.value["ell1_times_minus_exclusion"]
        self.assertIn("strictly less than 2/sqrt(3)", exclusion["minus_gap_bound"])
        self.assertIn("no sum or difference", exclusion["conclusion"])

    def test_low_ell_audit(self) -> None:
        audit = self.value["finite_low_ell_audit"]
        self.assertTrue(audit["all_residuals_nonzero"])
        self.assertEqual(len(audit["comparisons"]), 14)

    def test_bounded_class_is_obstructed(self) -> None:
        self.assertEqual(self.value["correction_classes"]["BOUNDED_SMOOTH_UNIFORMLY_ALMOST_PERIODIC"]["status"], "OBSTRUCTED")

    def test_generic_nonminus_gate_remains_open(self) -> None:
        self.assertFalse(self.value["classification"]["generic_ell_ge_2_nonminus_oscillators_classified"])


if __name__ == "__main__":
    unittest.main()
