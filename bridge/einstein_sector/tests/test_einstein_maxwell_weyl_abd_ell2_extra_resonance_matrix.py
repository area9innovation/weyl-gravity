from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json"


class AbdResonanceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_all_four_chains_have_rank_three(self) -> None:
        self.assertTrue(
            self.value["classification"][
                "every_parity_polarization_abd_polynomial_chain_rank_three"
            ]
        )

    def test_remaining_columns_and_pde_gate_fail_closed(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["twist_position_velocity_columns_computed"])
        self.assertFalse(classification["complete_homogeneous_twist_source_matrix"])
        self.assertFalse(classification["full_second_order_equation_solved"])


if __name__ == "__main__":
    unittest.main()
