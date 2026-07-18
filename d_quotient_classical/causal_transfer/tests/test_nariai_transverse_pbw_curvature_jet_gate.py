from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_PBW_CURVATURE_JET_GATE_V1.json"


class TransversePBWCurvatureJetGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_curvature_is_not_parallel(self) -> None:
        witness = self.value["exact_data"]["curvature_jet"]["nonparallel_witness"]
        self.assertEqual(witness["component"], "nabla_0 delta C_0202")
        self.assertEqual(witness["value"], "-sqrt(2)")

    def test_parallel_middle_is_not_authoritative(self) -> None:
        audit = self.value["exact_data"]["frozen_parallel_PBW_audit"]
        self.assertFalse(audit["authoritative_for_true_transverse_middle"])
        self.assertTrue(audit["square_matches_independent_curvature_action"])
        self.assertEqual(audit["variations"]["yang_mills_middle"]["nonzero_coefficients"], 126)
        self.assertEqual(audit["variations"]["compressed_middle"]["nonzero_coefficients"], 130)

    def test_downstream_is_fail_closed(self) -> None:
        self.assertFalse(self.value["flags"]["TRANSVERSE_MIDDLE_SCHUR_VARIATION"])
        self.assertFalse(self.value["flags"]["TRANSVERSE_CAUSAL_TRANSFER"])


if __name__ == "__main__":
    unittest.main()
