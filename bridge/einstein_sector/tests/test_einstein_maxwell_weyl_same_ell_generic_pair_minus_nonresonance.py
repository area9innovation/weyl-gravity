from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class SameEllGenericPairMinusNonresonanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_same_ell_generic_pair_minus_nonresonance.json").read_text())

    def test_difference_bound(self) -> None:
        difference = self.value["difference_exclusion"]
        self.assertIn("159/100", difference["ell_at_least_3_bound"])
        self.assertIn("18-10sqrt(3)", difference["ell_2_direct_witness"])

    def test_sum_bracket(self) -> None:
        sums = self.value["sum_exclusion"]
        self.assertIn("w(2ell-1)<2*w(ell)<w(2ell)", sums["minus_minus"])
        self.assertIn("above the largest", sums["conclusion"])

    def test_all_branch_pairs(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["all_six_unordered_branch_pairs_covered"])
        self.assertTrue(classification["all_sum_and_difference_channels_covered"])

    def test_combined_generic_pair_theorem(self) -> None:
        self.assertTrue(self.value["classification"]["combined_all_generic_input_ell_pairs_minus_nonresonant"])

    def test_exceptional_generic_gate_remains_open(self) -> None:
        self.assertFalse(self.value["classification"]["exceptional_ell1_times_generic_pairs_classified"])


if __name__ == "__main__":
    unittest.main()
