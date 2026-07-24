#!/usr/bin/env python3
"""Mutation tests for the ECS inverse-tortoise certificate."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify

HERE = Path(__file__).resolve().parent


class EcsInverseTortoiseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_passes(self) -> None:
        self.assertEqual(verify(self.document), [])

    def test_slope_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["inverse_tortoise_branch"][
            "real_part_slope_rational_lower"
        ] = "3/4"
        self.assertTrue(verify(mutant))

    def test_operator_norm_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["volterra"]["channels"][0]["operator_norm_upper"] = "0"
        self.assertTrue(verify(mutant))

    def test_potential_integral_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["volterra"]["channels"][1][
            "potential_integral_upper"
        ] = "1"
        self.assertTrue(verify(mutant))

    def test_false_evans_promotion_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["claim_flags"]["Evans_boundary_nonzero_certified"] = True
        self.assertTrue(verify(mutant))

    def test_false_full_frame_promotion_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["claim_flags"]["full_bach_outgoing_frame_constructed"] = True
        self.assertTrue(verify(mutant))


if __name__ == "__main__":
    unittest.main()
