"""Tests for the exceptional/ell2-extra difference matrix."""

from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "bridge/certificates/einstein_maxwell_weyl_exceptional_ell1_ell2_extra_difference_matrix.json"


class ExceptionalDifferenceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_all_eight_columns_are_present(self) -> None:
        self.assertEqual(len(self.record["direct_source_rows"]), 8)
        self.assertEqual(len(self.record["adjoint_projections"]), 8)

    def test_sparse_support_is_exact(self) -> None:
        nonzero = {key: value for key, value in self.record["adjoint_projections"].items() if value != "0"}
        self.assertEqual(nonzero, {"axial/polar/e2": "-768/5", "polar/polar/e2": "-864/5"})

    def test_one_control_amplitude_survives(self) -> None:
        self.assertEqual(self.record["sparse_matrix"]["unique_control_amplitude"], "ell2 polar e2")
        self.assertTrue(self.record["classification"]["unique_ell2_polar_e2_control_amplitude"])

    def test_joint_d_equations_are_exposed(self) -> None:
        equations = self.record["joint_d_equations"]
        self.assertIn("768/5", equations["axial_L1"])
        self.assertIn("864/5", equations["polar_L1"])

    def test_higher_scopes_remain_open(self) -> None:
        classification = self.record["classification"]
        self.assertFalse(classification["SO3_all_m_tensor_assembled"])
        self.assertFalse(classification["exceptional_L2_self_and_d_control_solved_jointly"])
        self.assertFalse(classification["complete_exceptional_mixed_bounded_zero_locus_solved"])
        self.assertFalse(classification["causal_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
