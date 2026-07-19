from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class AxialAxialL4MatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(
            (ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_axial_L4_matrix.json").read_text()
        )

    def test_complete_axial_axial_basis_matrix(self) -> None:
        summary = self.value["matrix_summary"]
        self.assertEqual(summary["candidate_rows"], 12)
        self.assertEqual(summary["axial_input_basis_fixtures"], 20)
        self.assertEqual(summary["target_adjoint_coefficients"], 27)

    def test_exactly_one_scalar_component_vanishes(self) -> None:
        summary = self.value["matrix_summary"]
        self.assertEqual(summary["zero_target_adjoint_coefficients"], 1)
        self.assertEqual(summary["nonzero_target_adjoint_coefficients"], 26)

    def test_every_basis_fixture_has_a_nonzero_cokernel_vector(self) -> None:
        fixtures = [
            fixture
            for row in self.value["candidate_rows"]
            for fixture in row["basis_fixtures"]
        ]
        self.assertEqual(len(fixtures), 20)
        self.assertTrue(all(fixture["bounded_status"] == "OBSTRUCTED" for fixture in fixtures))
        self.assertTrue(all(fixture["witness_interval"]["excludes_zero"] for fixture in fixtures))

    def test_correction_classes_remain_distinct(self) -> None:
        verdict = self.value["second_order_verdict"]
        self.assertEqual(verdict["bounded_or_finite_quasiperiodic_basis_fixtures"], "OBSTRUCTED")
        self.assertEqual(verdict["smooth_secular_status"], "OPEN")
        self.assertEqual(verdict["causal_retarded_status"], "NO_CERTIFIED_MAP")

    def test_workload_and_cone_are_fail_closed(self) -> None:
        progress = self.value["workload_progress"]
        self.assertEqual(progress["resolved_axisymmetric_L4_coefficients"], 27)
        self.assertEqual(progress["remaining_axisymmetric_L4_coefficients"], 81)
        self.assertEqual(progress["remaining_nonaxisymmetric_L1_L3_coefficients"], 56)
        self.assertFalse(progress["complete_two_fibre_tangent_cone_classified"])
        self.assertFalse(self.value["classification"]["arbitrary_axial_linear_combinations_classified"])


if __name__ == "__main__":
    unittest.main()
