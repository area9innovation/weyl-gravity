"""Tests for the finite-generic smooth-global second-order theorem."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_finite_generic_smooth_global_second_order import DEFAULT_OUTPUT, build_certificate


class FiniteGenericSmoothGlobalTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8")), self.payload)

    def test_arbitrary_finite_generic_carrier_is_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["arbitrary_finite_generic_harmonic_sums_classified_smooth_global"])
        self.assertTrue(classification["multiple_absolute_momentum_fibres_classified_smooth_global"])
        self.assertTrue(classification["opposite_momenta_and_all_relative_phases_included"])

    def test_cokernel_split_is_correction_class_sensitive(self) -> None:
        classes = self.payload["correction_classes"]
        self.assertEqual(classes["SMOOTH_SECULAR"]["status"], "CERTIFIED")
        self.assertEqual(classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "CERTIFIED_FORMULA_ZERO_LOCUS_OPEN")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")

    def test_scope_remains_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["exceptional_or_global_input_modes_included"])
        self.assertFalse(classification["infinite_harmonic_completion_classified"])
        self.assertFalse(classification["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
