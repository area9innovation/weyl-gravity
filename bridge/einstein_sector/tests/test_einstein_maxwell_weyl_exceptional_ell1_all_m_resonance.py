"""Tests for the all-m exceptional ell=1 resonance no-go."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_all_m_resonance import DEFAULT_OUTPUT


class AllMExceptionalResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_zero_locus(self) -> None:
        zero_locus = self.payload["compatibility_zero_locus"]
        self.assertTrue(zero_locus["zero_dimensional"])
        self.assertEqual(zero_locus["common_zero_locus"], "a=p=0")

    def test_all_m_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["distinct_m_interference_classified"])
        self.assertTrue(classification["complete_all_m_exceptional_ell1_two_polarization_cone_second_order_obstructed"])

    def test_global_zero_modes_do_not_help(self) -> None:
        self.assertTrue(self.payload["classification"]["generalized_zero_global_balances_cannot_remove_2omega_obstruction"])

    def test_external_same_frequency_gate_open(self) -> None:
        self.assertFalse(self.payload["classification"]["same_frequency_nonexceptional_cancellation_classified"])


if __name__ == "__main__":
    unittest.main()
