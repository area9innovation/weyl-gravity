from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_smooth_secular_second_order.json"


class GlobalExtraSmoothSecularSecondOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_correction_classes_are_separated(self) -> None:
        classes = self.value["correction_classes"]
        self.assertTrue(classes["bounded_or_finite_quasiperiodic"].startswith("OBSTRUCTED"))
        self.assertTrue(classes["smooth_exponential_polynomial"].startswith("CERTIFIED"))
        self.assertTrue(classes["causal_or_retarded"].startswith("NO_CERTIFIED_MAP"))

    def test_complete_channel_ledger(self) -> None:
        self.assertEqual(
            set(self.value["channel_ledger"]),
            {"global_global", "extra_conjugate_self", "extra_sum", "ell0_extra_cross", "aligned_twist_extra_cross"},
        )
        self.assertEqual(self.value["channel_ledger"]["ell0_extra_cross"]["divisors"]["p"], "0")
        self.assertEqual(self.value["channel_ledger"]["aligned_twist_extra_cross"]["L3_divisors"]["p"], "-6")

    def test_no_later_lifecycle_promotion(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["aligned_twist_extra_L1_L3_correction_coefficient_explicit"])
        self.assertFalse(flags["coefficient_explicit_correction_printed"])
        self.assertFalse(flags["causal_retarded_map_certified"])
        self.assertFalse(flags["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
