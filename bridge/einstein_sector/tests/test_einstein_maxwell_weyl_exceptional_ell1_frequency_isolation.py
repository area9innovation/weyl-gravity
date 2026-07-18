"""Tests for exceptional ell=1 same-frequency isolation."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_exceptional_ell1_frequency_isolation import DEFAULT_OUTPUT


class ExceptionalFrequencyIsolationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(DEFAULT_OUTPUT).read_text(encoding="utf-8"))

    def test_generic_blocks_are_separated(self) -> None:
        self.assertTrue(self.payload["classification"]["all_k0_generic_axial_and_polar_p_q_primaries_frequency_separated"])

    def test_same_frequency_block_is_complete(self) -> None:
        self.assertTrue(self.payload["classification"]["exceptional_ell1_same_frequency_eigenspace_complete"])

    def test_pure_exceptional_no_go_is_frozen(self) -> None:
        self.assertTrue(self.payload["classification"]["complete_pure_exceptional_ell1_k0_second_order_no_go_frozen"])

    def test_broader_resonances_remain_open(self) -> None:
        self.assertFalse(self.payload["classification"]["different_frequency_pair_sums_classified"])
        self.assertFalse(self.payload["classification"]["different_momentum_pairs_classified"])


if __name__ == "__main__":
    unittest.main()
