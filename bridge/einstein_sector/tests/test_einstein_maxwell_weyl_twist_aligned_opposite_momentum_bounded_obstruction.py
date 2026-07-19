from __future__ import annotations

import json
from pathlib import Path
import unittest

from bridge.einstein_sector.verify_einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction import verify


ROOT = Path(__file__).resolve().parents[3]
PAYLOAD = ROOT / "bridge/certificates/einstein_maxwell_weyl_twist_aligned_opposite_momentum_bounded_obstruction.json"


class TwistAlignedOppositeMomentumBoundedObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(PAYLOAD.read_text(encoding="utf-8"))

    def test_fast_independent_verifier(self) -> None:
        verify()

    def test_correction_classes_remain_distinct(self) -> None:
        classes = self.payload["correction_classes"]
        self.assertEqual(classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OBSTRUCTED")
        self.assertEqual(classes["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"], "CERTIFIED")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")

    def test_scope_is_not_generalized(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["polar_L4_p_adjoint_pairing_nonzero"])
        self.assertFalse(classification["general_bounded_zero_locus_classified"])
        self.assertFalse(classification["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
