"""Scoped tests for the panels 0--97 aggregate."""
from __future__ import annotations

import unittest

from .aggregate import compute


class ProjectiveAggregateV10Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = compute()

    def test_contiguous_prefix(self) -> None:
        self.assertEqual(
            [row["panel"] for row in self.result["rows"]],
            list(range(98)),
        )

    def test_completed_rows_pass(self) -> None:
        for row in self.result["rows"]:
            self.assertTrue(all(row["interface_gates"].values()))
            self.assertTrue(row["delta"]["excludes_zero"])

    def test_terminal_panel(self) -> None:
        gate = self.result["local_qnm_gate"]
        obstruction = gate["first_obstruction"]
        self.assertEqual(obstruction["first_missing_panel"], 98)
        self.assertEqual(
            obstruction["code"],
            "COMMON_AFFINE_DELTA_ENCLOSURE_CONTAINS_ZERO",
        )
        self.assertFalse(gate["interval_newton_run"])


if __name__ == "__main__":
    unittest.main()
