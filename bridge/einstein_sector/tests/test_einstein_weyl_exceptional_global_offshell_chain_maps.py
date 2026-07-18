from __future__ import annotations

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_weyl_exceptional_global_offshell_chain_maps import build
from bridge.einstein_sector.verify_einstein_weyl_exceptional_global_offshell_chain_maps import verify


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/EINSTEIN_WEYL_EXCEPTIONAL_GLOBAL_OFFSHELL_CHAIN_MAPS_V1.json"


class ExceptionalGlobalOffshellChainMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_generator_is_fresh(self) -> None:
        self.assertEqual(self.value, build())

    def test_independent_replay(self) -> None:
        self.assertEqual(verify()["status"], "PASS")

    def test_all_exceptional_blocks_are_present(self) -> None:
        self.assertEqual(set(self.value["blocks"]), {"axial_ell1", "polar_ell1", "polar_ell0"})
        for block in self.value["blocks"].values():
            self.assertEqual(set(block["defects"].values()), {"0"})
            self.assertEqual(block["inverted_polynomials"], [])

    def test_global_triangle_remains_fail_closed(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["all_harmonic_sector_coefficient_maps_available"])
        self.assertFalse(flags["single_covariant_support_local_map_reconstructed"])
        self.assertFalse(flags["support_local_global_mapping_cofiber_certified"])
        self.assertFalse(flags["EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1_certified"])


if __name__ == "__main__":
    unittest.main()
