"""Scoped tests for the panel-77 horizon center repair."""
from __future__ import annotations

import json
import unittest

from flint import arb

from .repair import RUN


class HorizonCenterRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(RUN.read_text())
        cls.grid = {
            row["label"]: row
            for row in cls.document["diagnostic_grid"]
        }

    def test_failure_is_cancellation_not_precision_or_order(self) -> None:
        self.assertTrue(self.grid["box_baseline"]["self_map_passed"])
        for label in (
            "center_baseline",
            "center_higher_precision",
            "center_higher_seed_and_taylor_order",
        ):
            self.assertFalse(self.grid[label]["self_map_passed"])
            self.assertEqual(
                self.grid[label]["failure"],
                "HORIZON_Q_REMAINDER_SELF_MAP",
            )

    def test_stable_root_proves_strict_self_map(self) -> None:
        stable = self.grid["center_stable_interval_root"]
        self.assertTrue(stable["self_map_passed"])
        self.assertGreater(arb(stable["strict_margin"]).lower(), 0)
        self.assertFalse(self.document["repair"]["threshold_lowered"])

    def test_reciprocal_pivots_are_certified(self) -> None:
        for pivot in self.document["reciprocal_chart"]:
            self.assertTrue(pivot["pivot_excludes_zero"])
            self.assertGreater(
                arb(pivot["q_modulus_lower"]).lower(), 0
            )

    def test_repaired_panel_is_nonzero(self) -> None:
        panel = self.document["repaired_panel"]
        self.assertEqual(
            panel["boundary_nonvanishing"]["status"], "PASS"
        )
        self.assertGreater(
            arb(panel["physical_mismatch"]["modulus_lower"]).lower(), 0
        )


if __name__ == "__main__":
    unittest.main()
