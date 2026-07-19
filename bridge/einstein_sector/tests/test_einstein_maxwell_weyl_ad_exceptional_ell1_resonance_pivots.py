"""Tests for the exceptional ell=1 a,d pivot certificate."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

import sympy as sp


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_ad_exceptional_ell1_resonance_pivots.json"


class ExceptionalADPivotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_scope_is_fully_typed(self) -> None:
        scope = self.record["scope"]
        self.assertEqual(scope["ell"], "0 x 1 -> 1")
        self.assertEqual(scope["k"], 0)
        self.assertEqual(scope["omega"], "omega_exceptional^2=4/3")

    def test_axial_pivots_are_nonzero(self) -> None:
        values = self.record["projected_adjoint_polynomials"]["axial"]
        self.assertIn("t", values["a"])
        self.assertNotEqual(sp.sympify(values["d"], locals={"I": sp.I, "sqrt": sp.sqrt}), 0)

    def test_polar_pivots_are_nonzero(self) -> None:
        values = self.record["projected_adjoint_polynomials"]["polar"]
        self.assertIn("t", values["a"])
        self.assertNotEqual(sp.sympify(values["d"], locals={"I": sp.I, "sqrt": sp.sqrt}), 0)

    def test_live_collision_is_fail_closed(self) -> None:
        classification = self.record["classification"]
        self.assertTrue(classification["exceptional_times_ell2_extra_difference_collision_open"])
        self.assertFalse(classification["complete_exceptional_mixed_bounded_zero_locus_solved"])

    def test_no_causal_or_quantum_promotion(self) -> None:
        self.assertFalse(self.record["classification"]["causal_or_quantum_claim"])
        self.assertIn("not the complete exceptional mixed bounded cone", self.record["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
