from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import unittest

from d_quotient_classical.compensator.verify_degenerate_curvature_coupling_level3_no_go import (
    verify,
)


ROOT = Path(__file__).resolve().parents[3]
CERTIFICATE = (
    ROOT
    / "d_quotient_classical/certificates/"
    "COMPENSATOR_DEGENERATE_CURVATURE_COUPLING_LEVEL3_NO_GO_V1.json"
)


class DegenerateCurvatureCouplingLevel3NoGoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(CERTIFICATE.read_text())

    def test_independent_raw_flrw_replay(self) -> None:
        verify(deepcopy(self.value))

    def test_literal_hessian_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["exact_adm_degeneracy"]["literal_work_item_pair"][
            "velocity_Hessian"
        ]["entries"][0]["coefficient"] = "1"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_intersection_basis_mutation_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["complete_literal_locus"]["groebner_basis"][1] = "2f1"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_nonempty_good_locus_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["complete_literal_locus"]["good_locus"] = "NONEMPTY"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_selected_action_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["terminal_verdict"]["selected_level3_action"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_full_unary_promotion_rejected(self) -> None:
        mutated = deepcopy(self.value)
        mutated["claim_flags"]["FULL_ACTION_ORIGIN_BV_UNARY"] = True
        with self.assertRaises(Exception):
            verify(mutated)

    def test_control_cannot_become_literal_theorem(self) -> None:
        mutated = deepcopy(self.value)
        mutated["convention_correct_control"]["constant_clock_cylinder"][
            "trace_lapse_repair"
        ] = "CERTIFIED"
        with self.assertRaises(Exception):
            verify(mutated)

    def test_quantum_and_general_no_go_promotions_rejected(self) -> None:
        for key in (
            "GENERAL_HORNDESKI_DHOST_NO_GO",
            "HADAMARD_ANOMALY_QME_OR_QUANTUM",
        ):
            with self.subTest(key=key):
                mutated = deepcopy(self.value)
                mutated["claim_flags"][key] = True
                with self.assertRaises(Exception):
                    verify(mutated)


if __name__ == "__main__":
    unittest.main()
