"""Scoped materialized tests for adaptive continuation v3."""
from __future__ import annotations

import json
import unittest
from fractions import Fraction

from .continuation import AGGREGATE_RUN, RAW_RUN, canonical_sha


class AdaptiveContinuationV3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = json.loads(RAW_RUN.read_text())
        cls.aggregate = json.loads(AGGREGATE_RUN.read_text())

    def test_budget_and_imported_parent(self) -> None:
        self.assertLess(self.raw["elapsed_compute_seconds"], 60)
        first = self.raw["observations"][0]
        self.assertEqual(first["kind"], "imported_parent_observation")
        self.assertEqual(first["parent_panel"], 101)
        self.assertEqual(first["row_sha256"], canonical_sha(first["row"]))

    def test_exact_contiguous_coverage(self) -> None:
        bounds = [
            (Fraction(item["start"]), Fraction(item["stop"]))
            for item in self.aggregate["segments"]
        ]
        self.assertTrue(all(
            left[1] == right[0]
            for left, right in zip(bounds, bounds[1:])
        ))

    def test_root_and_smith_closed(self) -> None:
        self.assertFalse(any(self.aggregate["closed_claim_gates"].values()))


if __name__ == "__main__":
    unittest.main()
