"""Scoped tests for the contiguous projective Evans aggregate."""
from __future__ import annotations

import unittest

from .aggregate import compute


class ProjectiveAggregateV4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = compute()

    def test_contiguous_prefix(self) -> None:
        rows = self.result["rows"]
        self.assertEqual([row["panel"] for row in rows], list(range(32)))
        self.assertTrue(self.result["summary"]["contiguous_prefix"])

    def test_all_completed_rows_pass(self) -> None:
        for row in self.result["rows"]:
            self.assertTrue(all(row["interface_gates"].values()))
            self.assertTrue(row["delta"]["excludes_zero"])

    def test_next_gate_is_panel_32(self) -> None:
        gate = self.result["local_qnm_gate"]
        self.assertEqual(gate["status"], "FAIL_CLOSED")
        self.assertEqual(
            gate["first_obstruction"]["first_missing_panel"], 32
        )
        self.assertFalse(gate["interval_newton_run"])
        self.assertFalse(gate["argument_principle_run"])


if __name__ == "__main__":
    unittest.main()
