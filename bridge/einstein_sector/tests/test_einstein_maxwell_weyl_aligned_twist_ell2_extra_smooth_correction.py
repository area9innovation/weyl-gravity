import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_aligned_twist_ell2_extra_smooth_correction.json"


class AlignedTwistExtraSmoothCorrectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_complete_scoped_channel_count(self) -> None:
        cases = self.value["cases"]
        self.assertEqual(len(cases), 16)
        self.assertEqual(sum(case["status"] == "COEFFICIENT_EXPLICIT_SMOOTH_CORRECTION" for case in cases.values()), 13)
        self.assertEqual(sum(case["status"] == "ZERO_SOURCE" for case in cases.values()), 3)

    def test_full_action_remainders_vanish(self) -> None:
        for case in self.value["cases"].values():
            self.assertEqual(case["full_action_remainder"], ["0", "0", "0", "0"])

    def test_fail_closed_scope(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["aligned_twist_extra_L1_L3_block_coefficient_explicit"])
        self.assertFalse(flags["complete_arbitrary_orbit_correction_coefficient_explicit"])
        self.assertFalse(flags["bounded_correction_certified"])
        self.assertFalse(flags["causal_retarded_correction_certified"])
        self.assertFalse(flags["all_orders_integrability"])


if __name__ == "__main__":
    unittest.main()
