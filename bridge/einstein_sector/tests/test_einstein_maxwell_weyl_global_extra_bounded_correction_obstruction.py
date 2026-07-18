from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_global_extra_bounded_correction_obstruction.json"


class GlobalExtraBoundedCorrectionObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_bounded_class_is_obstructed_on_complete_orbit(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["complete_nonzero_extra_common_zero_orbit_covered"])
        self.assertTrue(flags["bounded_or_finite_quasiperiodic_correction_obstructed"])
        self.assertEqual(self.value["channel"]["orbit_coefficient"], "-7*(3*Q**2 + 4*X)/6")

    def test_other_correction_classes_remain_open(self) -> None:
        self.assertFalse(self.value["classification"]["smooth_exponential_polynomial_correction_constructed"])
        self.assertFalse(self.value["classification"]["causal_retarded_map_certified"])


if __name__ == "__main__":
    unittest.main()
