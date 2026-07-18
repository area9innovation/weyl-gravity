"""Tests for the aligned global self-source correction."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_global_orbit_self_second_order import OUTPUT


class GlobalOrbitSelfSecondOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(OUTPUT).read_text(encoding="utf-8"))

    def test_taub_condition_is_necessary_and_sufficient(self) -> None:
        self.assertTrue(self.payload["classification"]["global_self_second_order_extendible_iff_taub_condition"])

    def test_exceptional_and_generic_corrections_close(self) -> None:
        for block in ("polar_L1", "polar_L2"):
            self.assertEqual(set(self.payload["second_order_correction"][block]["all_eight_row_remainders"].values()), {"0"})

    def test_full_orbit_remains_fail_closed(self) -> None:
        self.assertFalse(self.payload["classification"]["full_global_extra_orbit_coefficient_explicit"])


if __name__ == "__main__":
    unittest.main()
