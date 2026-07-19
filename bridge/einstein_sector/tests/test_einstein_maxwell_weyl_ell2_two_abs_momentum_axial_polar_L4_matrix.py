from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class AxialPolarL4MatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(
            (
                ROOT
                / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_polar_L4_matrix.json"
            ).read_text()
        )

    def test_complete_forward_matrix(self) -> None:
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

    def test_direct_calibration(self) -> None:
        self.assertTrue(self.value["direct_calibration"]["exact_match"])

    def test_reverse_and_cone_stay_open(self) -> None:
        self.assertFalse(
            self.value["classification"]["reverse_input_order_matrix_classified"]
        )
        self.assertFalse(
            self.value["classification"]
            ["arbitrary_cross_parity_linear_combinations_classified"]
        )

    def test_correction_classes_remain_distinct(self) -> None:
        verdict = self.value["second_order_verdict"]
        self.assertEqual(verdict["smooth_secular_status"], "OPEN")
        self.assertEqual(verdict["causal_retarded_status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
