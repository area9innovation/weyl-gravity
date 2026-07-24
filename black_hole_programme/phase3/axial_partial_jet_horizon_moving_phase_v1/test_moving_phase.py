"""Scoped tests for the moving-phase horizon certificate."""
from __future__ import annotations

import json
import unittest

from . import produce, verify


class MovingPhaseTest(unittest.TestCase):
    def test_exact_data(self) -> None:
        crosswalk = json.loads(produce.INPUTS["partial_jet_crosswalk"].read_text())
        data = produce.exact_data(crosswalk)
        self.assertEqual(data["exponent_derivative"], 0)
        self.assertEqual(data["tangent_residue"], produce.sp.zeros(2))
        self.assertEqual(len(data["base"]), produce.ORDER + 1)
        self.assertEqual(len(data["tangent"]), produce.ORDER + 1)

    def test_fail_closed_boundary(self) -> None:
        doc = json.loads(produce.OUTPUT.read_text())
        self.assertTrue(doc["claim_flags"]["finite_mixed_seed_pass"])
        self.assertTrue(doc["claim_flags"]["uniform_frobenius_tail_enclosed"])
        self.assertTrue(doc["claim_flags"]["first_panel_transport_certified"])
        self.assertFalse(doc["claim_flags"]["T_plus_recovered"])

    def test_independent_verifier(self) -> None:
        verify.verify()


if __name__ == "__main__":
    unittest.main()
