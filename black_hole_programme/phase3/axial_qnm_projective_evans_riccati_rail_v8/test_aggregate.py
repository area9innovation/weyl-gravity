"""Scoped tests for the repaired panels 0--77 aggregate."""
from __future__ import annotations

import unittest

from .aggregate import compute


class ProjectiveAggregateV8Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = compute()

    def test_contiguous_prefix(self) -> None:
        self.assertEqual(
            [row["panel"] for row in self.result["rows"]],
            list(range(78)),
        )

    def test_completed_rows_pass(self) -> None:
        for row in self.result["rows"]:
            self.assertTrue(all(row["interface_gates"].values()))
            self.assertTrue(row["delta"]["excludes_zero"])

    def test_repaired_panel_and_next_missing(self) -> None:
        self.assertEqual(self.result["rows"][-1]["panel"], 77)
        gate = self.result["local_qnm_gate"]
        self.assertEqual(
            gate["first_obstruction"]["first_missing_panel"], 78
        )
        self.assertFalse(gate["interval_newton_run"])


if __name__ == "__main__":
    unittest.main()
