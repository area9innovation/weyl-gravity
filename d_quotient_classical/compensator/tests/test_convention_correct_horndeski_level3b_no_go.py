from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_convention_correct_horndeski_level3b_no_go import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = ROOT / "d_quotient_classical/certificates/COMPENSATOR_CONVENTION_CORRECT_HORNDESKI_LEVEL3B_NO_GO_V1.json"


class ConventionCorrectHorndeskiLevel3bNoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_raw_adm_cylinder_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_adm_hessian_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_adm_degeneracy"]["velocity_Hessian"]["entries"][0][
            "coefficient"
        ] = "1"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_slope_stationary_column_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["complete_cylinder_stationary_locus"]["stationary_matrix"][
            "entries"
        ].append({"row": 0, "column": 6, "coefficient": "1"})
        with self.assertRaises(Exception):
            verify(mutated)

    def test_clock_symbol_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["full_cylinder_quadratic_separator"]["clock_symbol"] = "0"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_nonempty_common_locus_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["stratified_no_go"]["common_seven_gate_good_locus"] = "NONEMPTY"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_selected_action_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["SELECTED_LEVEL3B_ACTION"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_berger_computation_promotion_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["BERGER_STATIONARY_LOCUS_COMPUTED"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_q2_and_quantum_promotions_rejected(self) -> None:
        for key in ("NONLINEAR_Q2", "HADAMARD_ANOMALY_QME_OR_QUANTUM"):
            with self.subTest(key=key):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][key] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
