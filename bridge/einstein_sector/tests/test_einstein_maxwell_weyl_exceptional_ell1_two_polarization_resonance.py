"""Tests for the axisymmetric exceptional two-polarization resonance no-go."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_two_polarization_resonance import DEFAULT_OUTPUT


class TwoPolarizationResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_self_pairing_cancellation(self) -> None:
        theorem = self.payload["resonance_theorem"]
        self.assertEqual(theorem["polar_self_adjoint_pairings"], ["1/8", "-1/4"])
        self.assertEqual(theorem["formal_self_pairing_cancellation_ratio"], "|a_p|^2=(16/3)*|a_x|^2")

    def test_cross_pairing(self) -> None:
        self.assertEqual(self.payload["resonance_theorem"]["axial_cross_adjoint_pairing"], "-8*sqrt(3)/9")

    def test_complete_axisymmetric_no_go(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["cross_channel_blocks_every_nonzero_two_polarization_cancellation"])
        self.assertTrue(classification["complete_axisymmetric_exceptional_ell1_two_polarization_cone_second_order_obstructed"])

    def test_all_m_open(self) -> None:
        self.assertFalse(self.payload["classification"]["all_m_exceptional_cone_classified"])


if __name__ == "__main__":
    unittest.main()
