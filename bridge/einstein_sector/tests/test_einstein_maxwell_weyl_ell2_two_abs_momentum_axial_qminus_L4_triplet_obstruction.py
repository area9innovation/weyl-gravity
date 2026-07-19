from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class AxialQminusL4TripletObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(
            (ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.json").read_text()
        )

    def test_triplet_scope_is_exact(self) -> None:
        self.assertEqual([row["candidate_index"] for row in self.value["triplet"]], [3, 4, 5])
        self.assertEqual([row["target_branch"] for row in self.value["triplet"]], ["q_minus", "p_extra", "q_plus"])
        self.assertTrue(all(row["bounded_status"] == "OBSTRUCTED" for row in self.value["triplet"]))

    def test_q_primary_witness_is_nonzero(self) -> None:
        witness = self.value["q_primary_common_nonzero_witness"]
        self.assertEqual(len(witness["annihilating_polynomial_coefficients"]), 5)
        self.assertEqual(witness["constant_term"], 480328793324440503975936)
        self.assertNotEqual(witness["constant_term"], 0)
        self.assertTrue(witness["zero_is_not_a_root"])

    def test_q_adjoint_is_symbolically_complete_on_both_q_roots(self) -> None:
        adjoint = self.value["q_primary_symbolic_adjoint"]
        self.assertEqual(adjoint["q_mass_polynomial"], "mu**2 - 40*mu + 360")
        self.assertEqual(adjoint["final_remainders"], ["0", "0", "0", "0"])
        self.assertTrue(all(row["target_block_rank"] == 3 for row in (self.value["triplet"][0], self.value["triplet"][2])))

    def test_correction_classes_are_fail_closed(self) -> None:
        verdict = self.value["second_order_verdict"]
        self.assertEqual(verdict["candidate_3"], "OBSTRUCTED")
        self.assertEqual(verdict["candidate_4"], "OBSTRUCTED")
        self.assertEqual(verdict["candidate_5"], "OBSTRUCTED")
        self.assertEqual(verdict["smooth_secular_status"], "OPEN")
        self.assertEqual(verdict["causal_retarded_status"], "NO_CERTIFIED_MAP")

    def test_workload_is_not_overpromoted(self) -> None:
        progress = self.value["workload_progress"]
        self.assertEqual(progress["resolved_axisymmetric_L4_coefficients"], 4)
        self.assertEqual(progress["remaining_axisymmetric_L4_coefficients"], 104)
        self.assertEqual(progress["remaining_nonaxisymmetric_L1_L3_coefficients"], 56)
        self.assertFalse(progress["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
