"""Regression tests for the all-ell k=0 output-resonance theorem."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_all_ell_k0_output_resonance import DEFAULT_OUTPUT, build_certificate


class AllEllK0OutputResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_all_frequency_channels_are_nonresonant(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["all_nine_frequency_types_covered"])
        self.assertTrue(classification["all_ell_at_least_2_covered"])
        self.assertTrue(classification["all_nonzero_output_channels_off_physical_target_shells"])

    def test_zero_source_gate_remains_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["zero_frequency_source_cokernel_classified"])
        self.assertFalse(classification["complete_all_ell_second_order_cone_proved"])


if __name__ == "__main__":
    unittest.main()
