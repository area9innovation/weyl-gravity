"""Regression tests for the exact bounded cross-ell resonance census."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_cross_ell_k0_resonance_census import DEFAULT_OUTPUT


class CrossEllK0ResonanceCensusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text())

    def test_certificate_contract(self) -> None:
        self.assertEqual(self.payload["result_state"], "EXACT_NO_RESONANCE_THROUGH_ELL_96")

    def test_exact_window_has_no_resonance(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["no_distinct_ell_frequency_collision_in_window"])
        self.assertTrue(classification["no_cross_ell_nonzero_output_resonance_in_window"])

    def test_census_cardinality(self) -> None:
        census = self.payload["census"]
        self.assertEqual(census["frequency_collision_checks"], 40185)
        self.assertEqual(census["squared_resonance_checks"], 723330)

    def test_unbounded_claim_remains_open(self) -> None:
        self.assertFalse(self.payload["classification"]["unbounded_cross_ell_theorem_proved"])
        self.assertFalse(self.payload["classification"]["cross_ell_quadratic_source_solved"])


if __name__ == "__main__":
    unittest.main()
