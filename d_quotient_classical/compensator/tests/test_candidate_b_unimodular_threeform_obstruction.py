from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_candidate_b_unimodular_threeform_obstruction import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical"
    / "certificates"
    / "COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1.json"
)


class CandidateBUnimodularThreeformObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_unit_cylinder_is_not_promoted(self) -> None:
        mutated = deepcopy(self.value)
        mutated["unit_cylinder_background_obstruction"][
            "simultaneous_equations_have_solution"
        ] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_tracefree_residual_mutation_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["unit_cylinder_background_obstruction"][
            "tracefree_Euler_matrix"
        ]["entries"][0]["coefficient"] = "0"
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_polynomial_kernel_mutation_is_detected(self) -> None:
        mutated = deepcopy(self.value)
        hessian = mutated["linearized_topological_block"]["Hessian"]
        next(
            entry
            for entry in hessian["entries"]
            if entry["row"] == 2 and entry["column"] == 1
        )["coefficient"] = "D"
        with self.assertRaises(AssertionError):
            verify(mutated)

    def test_compact_support_class_cannot_be_deleted(self) -> None:
        mutated = deepcopy(self.value)
        mutated["global_topology"]["compact_support_betti_Hc0_to_Hc4"] = [
            0,
            1,
            0,
            0,
            0,
        ]
        with self.assertRaises(Exception):
            verify(mutated)

    def test_spatial_flux_cannot_be_made_small_gauge(self) -> None:
        mutated = deepcopy(self.value)
        mutated["Berger_gate"]["small_gauge_compensator_exists"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_causal_parent_promotion_is_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["CANDIDATE_B_FULL_CAUSAL_PARENT"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_hadamard_promotion_is_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["HADAMARD_STATE"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_all_seven_gates_are_present(self) -> None:
        gates = self.value["seven_gate_disposition"]
        self.assertEqual([row["gate"] for row in gates], list(range(1, 8)))
        self.assertEqual(gates[1]["status"], "FAIL")
        self.assertEqual(gates[2]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
