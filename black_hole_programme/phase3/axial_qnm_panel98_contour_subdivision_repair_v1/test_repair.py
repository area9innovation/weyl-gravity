"""Scoped tests for the panel-98 subdivision repair."""
from __future__ import annotations

import json
import unittest
from fractions import Fraction

from flint import arb

from .repair import AGGREGATE_RUN, CHILD_RUN, canonical_sha


class Panel98SubdivisionRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.children = json.loads(CHILD_RUN.read_text())
        cls.aggregate = json.loads(AGGREGATE_RUN.read_text())

    def test_children_are_content_addressed_and_nonzero(self) -> None:
        self.assertEqual(
            [entry["panel"] for entry in self.children["children"]],
            [196, 197],
        )
        for entry in self.children["children"]:
            self.assertEqual(entry["row_sha256"], canonical_sha(entry["row"]))
            self.assertEqual(
                entry["row"]["boundary_nonvanishing"]["status"], "PASS"
            )
            self.assertGreater(
                arb(entry["row"]["physical_mismatch"]["modulus_lower"]).lower(),
                0,
            )

    def test_no_threshold_change(self) -> None:
        self.assertFalse(self.children["threshold_lowered"])

    def test_exact_parent_replacement(self) -> None:
        replacement = self.aggregate["replacement"]
        self.assertTrue(replacement["same_geometric_interval"])
        self.assertEqual(
            replacement["inserted_children"], ["196/1024", "197/1024"]
        )

    def test_repaired_prefix_and_next_gap(self) -> None:
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
        self.assertEqual(bounds[-1][1], Fraction(99, 512))
        self.assertEqual(
            self.aggregate["next_honest_boundary_gap"]["start"], "99/512"
        )

    def test_root_and_smith_claims_fail_closed(self) -> None:
        self.assertFalse(any(self.aggregate["closed_claim_gates"].values()))


if __name__ == "__main__":
    unittest.main()
