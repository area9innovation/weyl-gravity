"""Tests for the complete C4 extra-self correction ledger."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_extra_self_second_order import OUTPUT


class Ell2ExtraSelfSecondOrderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(Path(OUTPUT).read_text(encoding="utf-8"))

    def test_all_bilinear_generators_present(self) -> None:
        self.assertEqual(len(self.payload["bilinear_correction_ledger"]), 20)

    def test_all_nonstabilizer_blocks_close(self) -> None:
        for entry in self.payload["bilinear_correction_ledger"].values():
            for block in entry["blocks"].values():
                self.assertEqual(set(block["remainder"]), {"0"})

    def test_normalized_homogeneous_source_cancels(self) -> None:
        self.assertEqual(
            self.payload["normalization_bridge"]["combined_E00"],
            "beta**2-Q_e**2/2-(2/3)*X",
        )
        self.assertTrue(self.payload["classification"]["zero_homogeneous_component_cancels_with_global_source_on_cone"])


if __name__ == "__main__":
    unittest.main()
