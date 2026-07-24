#!/usr/bin/env python3
"""Mutation tests for the ECS inward scalar transport gate."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from .verify import verify

HERE = Path(__file__).resolve().parent


class EcsInwardTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_passes(self) -> None:
        self.assertEqual(verify(self.document), [])

    def test_generator_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["scalar_transport"]["generator_infinity_norm_upper"] = "1"
        self.assertTrue(verify(mutant))

    def test_matching_ball_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["scalar_transport"]["channels"][0]["matching_state_ball"][
            "common_radius"
        ] = "1"
        self.assertTrue(verify(mutant))

    def test_tangent_divisor_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["tangent_gate"][
            "real_path_apparent_divisor_modulus_lower"
        ] = "0"
        self.assertTrue(verify(mutant))

    def test_false_evans_promotion_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["claim_flags"]["Evans_boundary_nonzero_certified"] = True
        self.assertTrue(verify(mutant))

    def test_false_tangent_promotion_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["claim_flags"]["ecs_tangent_initializer_constructed"] = True
        self.assertTrue(verify(mutant))


if __name__ == "__main__":
    unittest.main()
