"""Regression tests for the same-parity ell=2 output ledger."""

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.einstein_maxwell_weyl_ell2_same_parity_output_resonance import DEFAULT_OUTPUT, build_certificate


class Ell2SameParityOutputResonanceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_certificate_current(self) -> None:
        self.assertEqual(json.loads(Path(DEFAULT_OUTPUT).read_text()), self.payload)

    def test_shared_ledger(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["same_parity_output_selection_certified"])
        self.assertTrue(classification["axial_and_polar_input_theorems_may_share_this_ledger"])

    def test_cross_scope_open(self) -> None:
        self.assertFalse(self.payload["classification"]["axial_polar_cross_parity_covered"])


if __name__ == "__main__":
    unittest.main()
