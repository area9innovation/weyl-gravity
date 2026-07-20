from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_kinetic_braiding_quadratic_visibility import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_KINETIC_BRAIDING_QUADRATIC_VISIBILITY_V1.json"
)


class KineticBraidingQuadraticVisibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_indexed_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_cylinder_metric_entry_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["unit_cylinder"]["complete_quadratic_Hessian"]["entries"].append(
            {"row": 0, "column": 1, "coefficient": "1"}
        )
        with self.assertRaises(Exception):
            verify(mutated)

    def test_Berger_symbol_sign_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["stationary_Berger"]["formal_symbol"]["matrix"]["entries"][0][
            "coefficient"
        ] = "-2*Delta"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_Berger_rank_promotion_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["stationary_Berger"]["formal_symbol"]["rank"][
            "every_nonzero_scalar_covector"
        ] = 4
        with self.assertRaises(Exception):
            verify(mutated)

    def test_boundary_term_cannot_be_retained_as_dynamics(self) -> None:
        mutated = deepcopy(self.value)
        mutated["stationary_Berger"]["boundary_terms_removed"][0] = (
            "NOT_REMOVED"
        )
        with self.assertRaises(Exception):
            verify(mutated)

    def test_cylinder_and_Berger_cannot_be_conflated(self) -> None:
        mutated = deepcopy(self.value)
        mutated["terminal_verdict"]["cylinder_quadratic_visibility"] = (
            "NONZERO_SCALAR_RANK_TWO"
        )
        with self.assertRaises(Exception):
            verify(mutated)

    def test_selected_action_promotion_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["SELECTED_LEVEL2_ACTION"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_quantum_and_causal_promotions_rejected(self) -> None:
        for key in (
            "COMPLETE_SUPPORT_LOCAL_CAUSAL_PARENT",
            "HADAMARD_ANOMALY_QME_OR_QUANTUM",
        ):
            with self.subTest(key=key):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][key] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
