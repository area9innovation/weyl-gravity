#!/usr/bin/env python3
"""Mutation tests for the infinity-tail negative gate."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify

HERE = Path(__file__).resolve().parent


class InfinityTailGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_passes(self) -> None:
        self.assertEqual(verify(self.document), [])

    def test_gain_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["scaled_tail_gate"]["gain_lower_at_first_order"] = "1"
        self.assertTrue(verify(mutant))

    def test_disk_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["disk"]["omega_modulus_l1_upper"] = "1"
        self.assertTrue(verify(mutant))

    def test_false_remainder_promotion_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["claim_flags"]["infinity_asymptotic_remainder_enclosed"] = True
        self.assertTrue(verify(mutant))

    def test_ecs_margin_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["ecs_replacement"]["delta"] = "0"
        self.assertTrue(verify(mutant))


if __name__ == "__main__":
    unittest.main()
