from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class PolarAxialL4MatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(
            (
                ROOT
                / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_axial_L4_matrix.json"
            ).read_text()
        )

    def test_complete_reverse_matrix(self) -> None:
        summary = self.value["matrix_summary"]
        self.assertEqual(summary["ordered_input_basis_fixtures"], 20)
        self.assertEqual(summary["target_adjoint_coefficients"], 27)
        self.assertEqual(summary["nonzero_target_adjoint_coefficients"], 27)

    def test_all_basis_fixtures_are_obstructed(self) -> None:
        self.assertEqual(
            self.value["matrix_summary"]
            ["basis_fixtures_with_nonzero_cokernel_vector"],
            20,
        )
        self.assertTrue(
            self.value["classification"]
            ["all_twenty_basis_fixtures_bounded_obstructed"]
        )

    def test_explicit_role_substitution_not_name_matching(self) -> None:
        audit = self.value["graded_symmetry_audit"]
        self.assertTrue(audit["reverse_matrix_obtained_by_explicit_role_substitution"])
        self.assertFalse(audit["name_based_mode_identification_used"])

    def test_all_axisymmetric_basis_coefficients_are_closed(self) -> None:
        progress = self.value["workload_progress"]
        self.assertEqual(progress["resolved_axisymmetric_L4_coefficients"], 108)
        self.assertEqual(progress["remaining_axisymmetric_L4_coefficients"], 0)
        self.assertEqual(progress["remaining_nonaxisymmetric_L1_L3_coefficients"], 56)

    def test_cone_and_causal_classes_stay_open(self) -> None:
        self.assertFalse(
            self.value["classification"]
            ["arbitrary_cross_parity_linear_combinations_classified"]
        )
        self.assertFalse(
            self.value["classification"]["complete_two_fibre_tangent_cone_classified"]
        )
        self.assertEqual(
            self.value["second_order_verdict"]["causal_retarded_status"],
            "NO_CERTIFIED_MAP",
        )


if __name__ == "__main__":
    unittest.main()
