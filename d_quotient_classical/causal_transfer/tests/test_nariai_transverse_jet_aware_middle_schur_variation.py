from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "d_quotient_classical/certificates/NARIAI_TRANSVERSE_JET_AWARE_MIDDLE_SCHUR_VARIATION_V1.json"


class TransverseJetAwareMiddleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text())

    def test_chain_variations_close(self) -> None:
        defects = self.value["exact_data"]["identity_defects"]
        self.assertEqual(defects["corrected_first_square_variation"]["nonzero_coefficients"], 0)
        self.assertEqual(defects["parent_YM_variation"]["nonzero_coefficients"], 0)
        self.assertGreater(defects["shifted_chain_variation"]["nonzero_coefficients"], 0)

    def test_curvature_jets_matter(self) -> None:
        comparison = self.value["exact_data"]["frozen_parallel_comparison"]
        self.assertTrue(comparison["coefficients_differ"])
        self.assertNotEqual(
            comparison["frozen_compressed_sha256"],
            comparison["jet_aware_compressed_sha256"],
        )
        operators = self.value["exact_data"]["operator_variations"]
        self.assertEqual(operators["unsupported_parent_identity_curvature_jet_words"], {})
        self.assertEqual(operators["unsupported_requested_curvature_jet_words"], {})
        self.assertTrue(self.value["flags"]["TRANSVERSE_COMPLETE_CURVATURE_JET_COVERAGE"])

    def test_schur_boundary(self) -> None:
        self.assertFalse(self.value["flags"]["TRANSVERSE_ALGEBRAIC_SCHUR_VARIATION"])
        gate = self.value["exact_data"]["differential_schur_gate"]
        self.assertFalse(gate["algebraic_qdot_sufficient"])
        self.assertTrue(any(len(word) != 1 for word in gate["non_algebraically_repairable_orders"]))
        self.assertFalse(self.value["flags"]["TRANSVERSE_ACTION_DERIVED_SCHUR_VARIATION"])
        self.assertFalse(self.value["flags"]["TRANSVERSE_CAUSAL_TRANSFER"])


if __name__ == "__main__":
    unittest.main()
