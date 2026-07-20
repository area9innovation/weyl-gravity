from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_kinetic_braiding_level2_no_go import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_KINETIC_BRAIDING_LEVEL2_NO_GO_V1.json"
)


class KineticBraidingLevel2NoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_integer_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_beta_column_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["complete_stationary_locus"]["extended_stacked_matrix"][
            "entries"
        ].append({"row": 0, "column": 6, "coefficient": "1"})
        with self.assertRaises(Exception):
            verify(mutated)

    def test_kernel_ray_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["complete_stationary_locus"]["kernel_basis"]["P2_ray"][0] = (
            "82/20"
        )
        with self.assertRaises(Exception):
            verify(mutated)

    def test_pure_braiding_cylinder_rank_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["independent_cylinder_zero_replay"]["braiding_rank"] = 1
        with self.assertRaises(Exception):
            verify(mutated)

    def test_Berger_visibility_cannot_rescue_cylinder(self) -> None:
        mutated = deepcopy(self.value)
        mutated["stratified_gate_disposition"]["good_locus"] = "NONEMPTY"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_q2_promotion_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["terminal_verdict"]["nonlinear_q2_required"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_selected_action_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["SELECTED_LEVEL2_ACTION"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_universal_and_quantum_promotions_rejected(self) -> None:
        for key in (
            "UNIVERSAL_BRAIDING_HORNDESKI_OR_DHOST_NO_GO",
            "HADAMARD_ANOMALY_QME_OR_QUANTUM",
        ):
            with self.subTest(key=key):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][key] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
