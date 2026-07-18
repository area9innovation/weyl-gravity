from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CERT = ROOT / "bridge/certificates/einstein_weyl_homogeneous_solution_cofiber.json"


class HomogeneousSolutionCofiberTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERT.read_text(encoding="utf-8"))

    def test_solution_cofiber_is_zero_but_identity_is_not_symplectic(self) -> None:
        self.assertTrue(self.value["classification"]["homogeneous_solution_cofiber_zero"])
        self.assertEqual(self.value["action_derived_pairing"]["relative_endomorphism"], "R=I+N, rank(N)=2, N^2=0")

    def test_offshell_and_residual_gates_remain_open(self) -> None:
        flags = self.value["classification"]
        self.assertFalse(flags["homogeneous_offshell_chain_map_certified"])
        self.assertFalse(flags["large_gauge_and_final_residual_descent_certified"])


if __name__ == "__main__":
    unittest.main()
