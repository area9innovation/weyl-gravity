"""Mutation tests for the bounded Bplus4 diagnosis."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class Bplus4MutationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_verifies(self) -> None:
        verify(copy.deepcopy(self.document))

    def test_rejects_generator_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["transport"]["shared_generator"] = 1
        with self.assertRaises(Exception):
            verify(changed)

    def test_rejects_rank_drift(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["rank_preservation"]["rank_three_at_certified_radius"] = False
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_r4_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["Bplus4_at_r4_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)

    def test_rejects_tplus_promotion(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["claim_flags"]["T_plus_certified"] = True
        with self.assertRaises(RuntimeError):
            verify(changed)


if __name__ == "__main__":
    unittest.main()
