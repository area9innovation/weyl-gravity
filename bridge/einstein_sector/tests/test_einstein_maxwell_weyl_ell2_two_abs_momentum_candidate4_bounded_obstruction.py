from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class Candidate4BoundedObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(
            (ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.json").read_text()
        )

    def test_scope_is_one_cross_momentum_fixture(self) -> None:
        self.assertEqual(self.value["candidate"]["candidate_index"], 4)
        self.assertEqual(self.value["candidate"]["p_shell_defect"], "0")
        self.assertEqual(self.value["generality_level"], "G1_EXPLICIT_ELL2_TWO_ABS_MOMENTUM_FIXTURE")

    def test_pbw_projection_is_calibrated(self) -> None:
        projection = self.value["pbw_projection"]
        self.assertEqual(projection["relevant_q2_terms"], 842)
        self.assertTrue(projection["opposite_momentum_calibration_exact"])
        self.assertEqual(len(projection["opposite_momentum_calibration_source"]), 4)

    def test_complete_p_cokernel_has_nonzero_component(self) -> None:
        cokernel = self.value["polar_p_cokernel"]
        self.assertEqual(cokernel["target_block_rank"], 2)
        self.assertEqual(cokernel["cokernel_dimension"], 2)
        self.assertEqual(cokernel["pairings"][0], "0")
        self.assertNotEqual(cokernel["pairings"][1], "0")
        self.assertEqual(cokernel["quadratic_field_norm_witness"], 3622)

    def test_verdict_is_fail_closed_by_correction_class(self) -> None:
        verdict = self.value["second_order_verdict"]
        self.assertEqual(verdict["status"], "OBSTRUCTED")
        self.assertEqual(verdict["correction_class"], "BOUNDED_OR_FINITE_QUASIPERIODIC")
        self.assertEqual(verdict["smooth_secular_status"], "OPEN")
        self.assertEqual(verdict["causal_retarded_status"], "NO_CERTIFIED_MAP")

    def test_workload_is_not_overpromoted(self) -> None:
        progress = self.value["workload_progress"]
        self.assertEqual(progress["candidate_4_axial_axial_coefficients_resolved"], 2)
        self.assertEqual(progress["remaining_axisymmetric_L4_coefficients"], 106)
        self.assertFalse(progress["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
