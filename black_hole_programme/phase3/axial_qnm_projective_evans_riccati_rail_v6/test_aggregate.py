"""Scoped tests for the panels 0--63 aggregate."""
from __future__ import annotations

import unittest

from .aggregate import compute


class ProjectiveAggregateV6Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = compute()

    def test_contiguous_prefix(self) -> None:
        self.assertEqual(
            [row["panel"] for row in self.result["rows"]],
            list(range(64)),
        )

    def test_completed_rows_pass(self) -> None:
        for row in self.result["rows"]:
            self.assertTrue(all(row["interface_gates"].values()))
            self.assertTrue(row["delta"]["excludes_zero"])

    def test_next_missing_panel(self) -> None:
        gate = self.result["local_qnm_gate"]
        self.assertEqual(
            gate["first_obstruction"]["first_missing_panel"], 64
        )
        self.assertFalse(gate["interval_newton_run"])


if __name__ == "__main__":
    unittest.main()
