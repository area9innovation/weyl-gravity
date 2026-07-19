from __future__ import annotations

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.verify_einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix import verify


ROOT = Path(__file__).resolve().parents[3]
PAYLOAD = ROOT / "bridge/certificates/einstein_maxwell_weyl_opposite_momentum_ell2_parity_resonance_matrix.json"


class OppositeMomentumParityResonanceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))

    def test_independent_verifier(self) -> None:
        verify()

    def test_pure_and_mixed_verdicts(self) -> None:
        locus = self.payload["null_locus"]
        self.assertEqual(locus["pure_axial_verdict"], "OBSTRUCTED")
        self.assertEqual(locus["pure_polar_verdict"], "OBSTRUCTED")
        self.assertTrue(locus["mixed_L4_resonance_null_face_nonempty"])

    def test_full_bounded_claim_remains_open(self) -> None:
        self.assertEqual(self.payload["correction_classes"]["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OPEN")
        self.assertFalse(self.payload["classification"]["complete_bounded_second_order_extension_on_mixed_null_face"])


if __name__ == "__main__":
    unittest.main()
