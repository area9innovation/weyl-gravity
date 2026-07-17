"""Tests for unbounded generic-output cross-ell nonresonance."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_generic_output_nonresonance import DEFAULT_OUTPUT, build_certificate


class CrossEllGenericOutputNonresonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_unbounded_generic_output_theorem(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["all_distinct_generic_input_ells_covered"])
        self.assertTrue(classification["all_generic_output_ells_at_least_2_covered"])
        self.assertTrue(classification["all_nonzero_generic_output_channels_off_target_shells"])

    def test_five_families_excluded(self) -> None:
        self.assertEqual(len(self.payload["family_reduction"]["unordered_families"]), 5)
        self.assertTrue(self.payload["family_exclusions"]["all_five_families_excluded"])

    def test_exceptional_and_source_gates_remain_open(self) -> None:
        self.assertFalse(self.payload["classification"]["exceptional_output_L1_classified"])
        self.assertFalse(self.payload["classification"]["cross_ell_quadratic_source_solved"])


if __name__ == "__main__":
    unittest.main()
