from __future__ import annotations

import json
import unittest
from pathlib import Path

from . import pivot_switch


HERE = Path(__file__).resolve().parent


class PivotSwitchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads((HERE / "pivot-switch-run.json").read_text())

    def test_former_obstruction_reproduced(self) -> None:
        self.assertTrue(self.data["former_obstruction"]["reproduced"])
        self.assertEqual(
            self.data["former_obstruction"]["failure"]["gate"],
            "PIVOT_CONTAINS_ZERO",
        )

    def test_fixed_gl_chart_and_exact_dual_gauge(self) -> None:
        switch = self.data["switch"]
        self.assertEqual(switch["determinant"], "1")
        self.assertEqual(switch["selected_row"], "e2-e3")
        self.assertEqual(switch["pivot"]["exact_base_pivot"], "1")
        self.assertEqual(switch["pivot"]["exact_tangent_pivot"], "0")

    def test_one_post_switch_panel(self) -> None:
        checkpoint = self.data["post_switch_checkpoint"]
        self.assertEqual(checkpoint["accepted_post_switch_panels"], 1)
        self.assertTrue(checkpoint["pivot"]["passed"])
        self.assertEqual(checkpoint["resume_payload"]["base"][2]["ball"], "1.00000000000000000000000000000000000000000000000000000000")
        self.assertEqual(checkpoint["resume_payload"]["tangent"][2]["ball"], "0")

    def test_recompute(self) -> None:
        self.assertEqual(pivot_switch.compute(), self.data)


if __name__ == "__main__":
    unittest.main()
