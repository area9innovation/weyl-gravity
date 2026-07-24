"""Scoped tests for the adaptive dyadic boundary chunk."""
from __future__ import annotations

import json
import unittest
from fractions import Fraction

from .adaptive import AGGREGATE_RUN, RAW_RUN, canonical_sha


class AdaptiveDyadicBoundaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = json.loads(RAW_RUN.read_text())
        cls.aggregate = json.loads(AGGREGATE_RUN.read_text())

    def test_budget_and_content_addresses(self) -> None:
        self.assertLess(self.raw["elapsed_compute_seconds"], 60)
        for entry in self.raw["observations"]:
            self.assertEqual(entry["row_sha256"], canonical_sha(entry["row"]))

    def test_ordered_parent_policy(self) -> None:
        parents = []
        for entry in self.raw["observations"]:
            if entry["kind"] == "parent_observation":
                parents.append(entry["parent_panel"])
        self.assertEqual(parents, list(range(99, 99 + len(parents))))

    def test_only_failed_parents_are_subdivided(self) -> None:
        by_parent = {
            entry["parent_panel"]: entry
            for entry in self.raw["observations"]
            if entry["kind"] == "parent_observation"
        }
        for entry in self.raw["observations"]:
            if entry["kind"] == "repair_child":
                parent = by_parent[entry["parent_panel"]]
                self.assertNotEqual(
                    parent["row"]["boundary_nonvanishing"]["status"], "PASS"
                )

    def test_contiguous_prefix(self) -> None:
        segments = self.aggregate["segments"]
        bounds = [
            (Fraction(item["start"]), Fraction(item["stop"]))
            for item in segments
        ]
        self.assertEqual(bounds[0][0], 0)
        self.assertTrue(all(
            left[1] == right[0]
            for left, right in zip(bounds, bounds[1:])
        ))

    def test_closed_claims(self) -> None:
        self.assertFalse(any(self.aggregate["closed_claim_gates"].values()))


if __name__ == "__main__":
    unittest.main()
