"""Mutation tests for the pointwise outgoing-population theorem."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify


HERE = Path(__file__).resolve().parent


class OutgoingPopulationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads((HERE / "certificate.json").read_text())

    def test_committed_certificate(self) -> None:
        verify(self.document)

    def test_frequency_mutation(self) -> None:
        bad = copy.deepcopy(self.document)
        bad["scope"]["frequency"] = "3/4"
        with self.assertRaises(Exception):
            verify(bad)

    def test_tplus_mutation(self) -> None:
        bad = copy.deepcopy(self.document)
        bad["claim_flags"]["Tplus_invertible_at_omega_half"] = False
        with self.assertRaises(Exception):
            verify(bad)

    def test_interval_overclaim_mutation(self) -> None:
        bad = copy.deepcopy(self.document)
        bad["claim_flags"][
            "whole_pilot_interval_outgoing_population_certified"
        ] = True
        with self.assertRaises(Exception):
            verify(bad)


if __name__ == "__main__":
    unittest.main()
