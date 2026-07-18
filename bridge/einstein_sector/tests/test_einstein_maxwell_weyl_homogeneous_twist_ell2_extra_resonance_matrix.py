from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_homogeneous_twist_ell2_extra_resonance_matrix.json"


class HomogeneousTwistResonanceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_twist_blocks_have_declared_ranks(self) -> None:
        theorem = self.value["twist_projection_theorem"]
        self.assertEqual(theorem["position_rank"], 2)
        self.assertEqual(theorem["velocity_rank_over_Q_sqrt3_i_t"], 4)
        self.assertTrue(theorem["velocity_determinant_nonzero_for_every_real_t"])

    def test_complete_matrix_does_not_promote_cone(self) -> None:
        flags = self.value["classification"]
        self.assertTrue(flags["complete_homogeneous_twist_bounded_resonance_matrix"])
        self.assertFalse(flags["simultaneous_stabilizer_and_resonance_zero_locus_solved"])
        self.assertFalse(flags["full_second_order_equation_solved"])


if __name__ == "__main__":
    unittest.main()
