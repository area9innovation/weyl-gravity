from __future__ import annotations

import json
import unittest
from pathlib import Path

from . import pivot_switch_continuation

HERE = Path(__file__).resolve().parent


class PivotSwitchContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(
            (HERE / "pivot-switch-continuation-run.json").read_text()
        )

    def test_progress_is_bounded_and_positive(self) -> None:
        self.assertEqual(self.data["accepted_panels_total"], 32)
        self.assertEqual(self.data["accepted_panels_from_switch_transition"], 6)
        self.assertEqual(self.data["last_valid_checkpoint"]["rho"], "3/8388608")

    def test_every_switch_is_serialized(self) -> None:
        self.assertEqual(self.data["switch_count"], len(self.data["switches"]))
        self.assertEqual(self.data["switch_count"], 1)
        switch = self.data["switches"][0]
        self.assertEqual(switch["selected"], "e2-e3")
        self.assertEqual(switch["pivot"]["exact_base_pivot"], "1")
        self.assertEqual(switch["pivot"]["exact_tangent_pivot"], "0")

    def test_honest_obstruction(self) -> None:
        self.assertEqual(
            self.data["terminal"]["gate"], "NONFINITE_TAYLOR_ENCLOSURE"
        )
        self.assertFalse(self.data["reached_next_dyadic_shell"])
        self.assertIsNone(self.data["checkpoint"])

    def test_recompute(self) -> None:
        self.assertEqual(pivot_switch_continuation.compute(), self.data)


if __name__ == "__main__":
    unittest.main()
