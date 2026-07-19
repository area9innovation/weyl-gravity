"""Tests for the complete finite-harmonic smooth-global tangent cone."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_complete_finite_harmonic_smooth_global_second_order import DEFAULT_OUTPUT, build_certificate


class CompleteFiniteHarmonicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8")), self.payload)

    def test_complete_inventory_is_included(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["complete_certified_linear_input_inventory_included"])
        self.assertTrue(classification["exceptional_and_global_inputs_included"])
        self.assertTrue(classification["complete_finite_harmonic_smooth_tangent_cone_classified"])

    def test_bounded_ledger_has_both_independent_parts(self) -> None:
        ledger = self.payload["bounded_obstruction_ledger"]
        self.assertIn("P_(j,r)", ledger["formula"])
        self.assertIn("R_(j,a)", ledger["formula"])
        self.assertEqual(ledger["coefficientwise_common_zero_locus"], "OPEN")

    def test_fail_closed_lifecycles(self) -> None:
        classes = self.payload["correction_classes"]
        self.assertEqual(classes["SMOOTH_SECULAR"]["status"], "CERTIFIED")
        self.assertEqual(classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "CERTIFIED_FORMULA_ZERO_LOCUS_OPEN")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")
        self.assertFalse(self.payload["classification"]["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
