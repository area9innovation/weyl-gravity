"""Scoped tests for the spin-one Levelt horizon package."""
from __future__ import annotations

import json
import unittest

from . import produce, verify


class SpinOneLeveltTest(unittest.TestCase):
    def test_exact_levelt_data(self) -> None:
        crosswalk = json.loads(produce.INPUTS["partial_jet_crosswalk"].read_text())
        data = produce.exact_data(crosswalk)
        self.assertEqual(data["tangent_residue"], produce.sp.zeros(4))
        self.assertEqual(data["residue"] * data["selected"], produce.sp.zeros(4, 1))
        self.assertEqual(len(data["resonance"]), 1)

    def test_tail_and_boundary(self) -> None:
        doc = json.loads(produce.OUTPUT.read_text())
        self.assertTrue(doc["claim_flags"]["spin_one_mixed_tail_enclosed"])
        self.assertTrue(doc["claim_flags"]["mixed_first_panel_transport_certified"])
        self.assertFalse(doc["claim_flags"]["multipanel_transport_certified"])
        self.assertFalse(doc["claim_flags"]["T_plus_recovered"])

    def test_independent_verifier(self) -> None:
        verify.verify()


if __name__ == "__main__":
    unittest.main()
