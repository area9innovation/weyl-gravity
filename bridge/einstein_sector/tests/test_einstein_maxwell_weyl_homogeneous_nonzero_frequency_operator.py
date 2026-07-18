"""Tests for the homogeneous nonzero-frequency Weyl-Maxwell operator."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_homogeneous_nonzero_frequency_operator import DEFAULT_OUTPUT


class HomogeneousNonzeroFrequencyOperatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_gauge_slice_complete(self) -> None:
        self.assertTrue(self.payload["classification"]["nonzero_frequency_gauge_slice_complete"])

    def test_quotient_empty(self) -> None:
        self.assertEqual(self.payload["operator_theorem"]["nonzero_frequency_quotient_dimension"], 0)

    def test_no_hidden_homogeneous_oscillator(self) -> None:
        self.assertTrue(self.payload["classification"]["homogeneous_extra_oscillatory_weyl_modes_absent"])


if __name__ == "__main__":
    unittest.main()
