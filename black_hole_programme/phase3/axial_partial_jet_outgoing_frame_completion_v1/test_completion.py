"""Mutation tests for the outgoing frame completion preflight."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class CompletionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = json.loads((HERE / "certificate.json").read_text())

    def test_certificate(self) -> None:
        verify(self.data)

    def test_refuses_tplus_promotion(self) -> None:
        broken = copy.deepcopy(self.data)
        broken["claim_flags"]["T_plus_certified"] = True
        with self.assertRaises(AssertionError):
            verify(broken)

    def test_refuses_correlated_S_promotion(self) -> None:
        broken = copy.deepcopy(self.data)
        broken["claim_flags"]["S_correlated_dual_remainder_certified"] = True
        with self.assertRaises(AssertionError):
            verify(broken)

    def test_refuses_basis_reorder(self) -> None:
        broken = copy.deepcopy(self.data)
        broken["normalized_columns"]["E"], broken["normalized_columns"]["R"] = (
            broken["normalized_columns"]["R"],
            broken["normalized_columns"]["E"],
        )
        with self.assertRaises(AssertionError):
            verify(broken)


if __name__ == "__main__":
    unittest.main()
