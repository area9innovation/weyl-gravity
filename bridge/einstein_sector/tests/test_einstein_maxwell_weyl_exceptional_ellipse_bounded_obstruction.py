from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ellipse_bounded_obstruction.json"


class ExceptionalEllipseBoundedObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_balanced_tangent_is_nonzero(self) -> None:
        self.assertTrue(self.value["classification"]["nonzero_stabilizer_balanced_tangent_explicit"])
        self.assertIn("d!=0", self.value["declared_tangent"]["ellipse_endpoint"])

    def test_unique_shell_pairing_is_nonzero(self) -> None:
        obstruction = self.value["unique_bounded_obstruction"]
        self.assertTrue(obstruction["nonzero"])
        self.assertIn("d times", obstruction["source_pair"])

    def test_correction_classes_are_separate(self) -> None:
        classes = self.value["correction_classes"]
        self.assertEqual(classes["BOUNDED_OR_FINITE_QUASIPERIODIC"]["status"], "OBSTRUCTED")
        self.assertEqual(classes["SMOOTH_EXPONENTIAL_POLYNOMIAL"]["status"], "CERTIFIED")
        self.assertEqual(classes["CAUSAL_RETARDED"]["status"], "NO_CERTIFIED_MAP")

    def test_scope_is_fail_closed(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["general_exceptional_mixed_zero_locus_classified"])
        self.assertFalse(flags["all_orders_integrability"])
        self.assertFalse(flags["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
