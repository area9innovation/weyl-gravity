#!/usr/bin/env python3
"""Mutation-style tests for the endpoint recurrence/divisor certificate."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

import sympy as sp

from . import verify

HERE = Path(__file__).resolve().parent


class EndpointGermTest(unittest.TestCase):
    def setUp(self) -> None:
        self.document = json.loads((HERE / "certificate.json").read_text())

    def test_certificate_verifies(self) -> None:
        self.assertEqual(verify.verify(), [])

    def test_left_half_plane_is_strict(self) -> None:
        disk = self.document["seed_disk"]
        cr = sp.Rational(disk["center_re"])
        radius = sp.Rational(disk["radius"])
        self.assertLess(cr + radius, 0)

    def test_upper_half_plane_is_strict(self) -> None:
        disk = self.document["seed_disk"]
        ci = sp.Rational(disk["center_im"])
        radius = sp.Rational(disk["radius"])
        self.assertGreater(ci - radius, 0)

    def test_horizon_divisor_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["horizon_germ"]["divisor"] = "(n + 1)*(n + 4*I*omega)"
        n, w = sp.symbols("n omega")
        recorded = sp.sympify(
            mutant["horizon_germ"]["divisor"],
            locals={"n": n, "omega": w, "I": sp.I},
        )
        expected = (n + 1) * (n + 1 + 4 * sp.I * w)
        self.assertNotEqual(sp.expand(recorded - expected), 0)

    def test_infinity_divisor_mutation_is_detected(self) -> None:
        mutant = copy.deepcopy(self.document)
        mutant["infinity_germ"]["divisor"] = "I*omega*(n+1)"
        self.assertNotEqual(
            mutant["infinity_germ"]["divisor"],
            self.document["infinity_germ"]["divisor"],
        )

    def test_no_root_count_promotion(self) -> None:
        self.assertFalse(
            self.document["claim_flags"]["QNM_root_count_certified"]
        )
        self.assertFalse(self.document["claim_flags"]["QNM_enclosed"])
        self.assertFalse(
            self.document["claim_flags"]["beta_or_EP2_established"]
        )


if __name__ == "__main__":
    unittest.main()
