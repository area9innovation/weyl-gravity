from __future__ import annotations

import json
import unittest
from pathlib import Path

from . import pivot_switch_subdivision_retry as retry

HERE = Path(__file__).resolve().parent


class PivotSwitchSubdivisionRetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(
            (HERE / "pivot-switch-subdivision-retry-run.json").read_text()
        )

    def test_corrected_checkpoint(self) -> None:
        checkpoint = self.data["corrected_last_valid_checkpoint"]
        self.assertEqual(checkpoint["panel"], 30)
        self.assertEqual(checkpoint["rho"], "95/268435456")

    def test_mutant_omitting_post_normalization_gate_is_killed(self) -> None:
        witness = self.data["panel_31_mutation_witness"]
        old_mutant = (
            witness["raw_taylor_state_finite"]
            and witness["pivot_gate_passed"]
        )
        corrected = retry.accepts_projective_step(
            witness["raw_taylor_state_finite"],
            witness["pivot_gate_passed"],
            witness["normalized_state_finite"],
        )
        self.assertTrue(old_mutant)
        self.assertFalse(corrected)
        self.assertFalse(witness["normalized_state_finite"])

    def test_retry_grid_is_complete(self) -> None:
        grid = self.data["retry_grid"]
        self.assertEqual(grid["orders"], list(retry.ORDERS))
        self.assertEqual(grid["subdivisions"], list(retry.SUBDIVISIONS))
        self.assertEqual(
            len(grid["attempts"]), len(retry.ORDERS) * len(retry.SUBDIVISIONS)
        )

    def test_retry_remains_fail_closed(self) -> None:
        attempts = self.data["retry_grid"]["attempts"]
        self.assertFalse(any(row["completed_full_panel"] for row in attempts))
        self.assertFalse(self.data["target"]["reached"])

    def test_recompute(self) -> None:
        self.assertEqual(retry.compute(), self.data)


if __name__ == "__main__":
    unittest.main()
