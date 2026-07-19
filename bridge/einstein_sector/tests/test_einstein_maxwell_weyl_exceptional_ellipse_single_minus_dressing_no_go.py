from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_single_minus_dressing_no_go.json"


class ExceptionalSingleMinusNoGoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_entire_ellipse_and_all_dressing_ell_are_covered(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["entire_axisymmetric_resonance_ellipse_covered"])
        self.assertTrue(flags["every_single_m0_Einstein_minus_dressing_ell_ge_2_covered"])
        self.assertTrue(flags["both_dressing_parities_covered"])

    def test_d_contradiction_is_explicit(self) -> None:
        obstruction = self.value["generic_obstruction"]
        self.assertIn("d!=0", obstruction["ellipse_fact"])
        self.assertIn("forces d=0", obstruction["contradiction"])

    def test_correction_classes_are_distinct(self) -> None:
        classes = self.value["correction_classes"]
        self.assertEqual(classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OBSTRUCTED")
        self.assertEqual(classes["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"], "CERTIFIED")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")

    def test_multiple_dressings_remain_open(self) -> None:
        self.assertFalse(self.value["classification"]["multiple_minus_modes_or_other_carriers_classified"])
        self.assertFalse(self.value["classification"]["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
