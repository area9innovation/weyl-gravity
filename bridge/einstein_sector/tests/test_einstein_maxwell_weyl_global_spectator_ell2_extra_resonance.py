"""Tests for global spectator removability."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_global_spectator_ell2_extra_resonance import DEFAULT_OUTPUT


class GlobalSpectatorResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_circumference_source_removable(self) -> None:
        self.assertTrue(self.payload["classification"]["circumference_times_ell2_extra_source_in_linear_image"])

    def test_wilson_source_zero(self) -> None:
        self.assertTrue(self.payload["classification"]["Wilson_times_ell2_extra_source_identically_zero"])

    def test_remaining_gate_explicit(self) -> None:
        self.assertFalse(self.payload["classification"]["remaining_homogeneous_a_b_d_Qe_cross_sources_classified"])
        self.assertFalse(self.payload["classification"]["remaining_twist_A_B_cross_sources_classified"])


if __name__ == "__main__":
    unittest.main()
