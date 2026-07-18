"""Tests for the exceptional positive-sum resonance census."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_resonance_census import DEFAULT_OUTPUT


class ExceptionalResonanceCensusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_positive_sum_census_complete(self) -> None:
        self.assertTrue(self.payload["classification"]["positive_sum_resonance_census_complete"])
        self.assertTrue(self.payload["classification"]["homogeneous_nonzero_frequency_target_empty"])

    def test_unique_live_block(self) -> None:
        self.assertEqual(
            self.payload["resonance_census"]["zero_plus_positive_inputs"]["unique_live_block"],
            "generic ell=2 extra p-primary, either parity, at k=0",
        )

    def test_source_gate_open(self) -> None:
        self.assertFalse(self.payload["classification"]["global_times_ell2_extra_source_pairing_computed"])

    def test_difference_gate_open(self) -> None:
        self.assertFalse(self.payload["classification"]["difference_frequency_resonances_classified"])


if __name__ == "__main__":
    unittest.main()
