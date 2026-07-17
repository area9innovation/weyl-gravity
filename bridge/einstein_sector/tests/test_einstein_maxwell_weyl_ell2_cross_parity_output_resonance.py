"""Regression tests for axial-polar ell=2 cross-output solvability."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_cross_parity_output_resonance import DEFAULT_OUTPUT, build_certificate


class Ell2CrossParityOutputResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_cross_blocks_invertible(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["cross_zero_frequency_physical_cokernel_absent"])
        self.assertTrue(classification["all_nine_cross_frequency_types_off_all_target_shells"])

    def test_no_coefficient_gate(self) -> None:
        self.assertFalse(self.payload["classification"]["cross_source_coefficients_required_for_solvability"])


if __name__ == "__main__":
    unittest.main()
