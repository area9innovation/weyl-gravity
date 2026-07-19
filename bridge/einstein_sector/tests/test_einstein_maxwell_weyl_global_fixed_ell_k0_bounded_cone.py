"""Tests for the global fixed-ell bounded cone."""

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_global_fixed_ell_k0_bounded_cone import OUTPUT, build


class GlobalFixedEllBoundedConeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(OUTPUT.read_text(encoding="utf-8")), self.value)

    def test_complete_union(self) -> None:
        self.assertTrue(self.value["complete_bounded_cone"]["union_is_necessary_and_sufficient"])

    def test_every_fixed_ell(self) -> None:
        self.assertTrue(self.value["classification"]["every_fixed_generic_ell_global_bounded_cone_classified"])

    def test_electric_witness_is_applied_after_wave_charge_cancellation(self) -> None:
        necessity = self.value["global_necessity"]
        self.assertEqual(necessity["electric_E11_replay"], "Q_e**2/2")
        self.assertIn("common H moment-map", necessity["electric_independence"])

    def test_fail_closed_cross_ell_and_momentum(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["cross_ell_superpositions_classified"])
        self.assertFalse(classification["nonzero_momentum_classified"])


if __name__ == "__main__":
    unittest.main()
