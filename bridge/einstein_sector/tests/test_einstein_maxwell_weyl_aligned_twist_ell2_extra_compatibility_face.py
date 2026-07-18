from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_compatibility_face.json"


class AlignedTwistExtraCompatibilityFaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_exact_nonzero_common_zero_face(self) -> None:
        self.assertTrue(self.value["classification"]["nonzero_simultaneous_stabilizer_and_bounded_resonance_zero_face"])
        self.assertEqual(self.value["explicit_nonzero_witness"]["X"], "1296")
        self.assertEqual(self.value["explicit_nonzero_witness"]["B_z"], "12*sqrt(6)")

    def test_full_zero_locus_and_corrections_remain_open(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["complete_simultaneous_zero_locus_classified"])
        self.assertFalse(flags["bounded_second_order_correction_constructed"])
        self.assertFalse(flags["smooth_secular_second_order_correction_constructed"])
        self.assertFalse(flags["causal_retarded_theorem"])


if __name__ == "__main__":
    unittest.main()
