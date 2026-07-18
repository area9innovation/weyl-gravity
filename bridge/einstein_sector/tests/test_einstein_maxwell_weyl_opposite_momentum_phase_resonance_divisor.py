"""Tests for the opposite-momentum phase resonance divisor."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_opposite_momentum_phase_resonance_divisor import DEFAULT_OUTPUT, build_certificate


class OppositeMomentumPhaseResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_universal_resonance_family(self) -> None:
        self.assertTrue(self.payload["classification"]["resonance_divisor_nonempty_for_every_ell"])

    def test_correction_space_split(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["bounded_or_finite_quasiperiodic_extension_follows_from_moment_maps_alone"])
        self.assertTrue(classification["generic_nonzero_resonance_removable_in_smooth_global_secular_class"])

    def test_static_exceptional_gate_open(self) -> None:
        self.assertFalse(self.payload["classification"]["static_L0_K2k_exceptional_block_classified"])
        self.assertFalse(self.payload["classification"]["complete_opposite_momentum_second_order_cone_classified"])


if __name__ == "__main__":
    unittest.main()
