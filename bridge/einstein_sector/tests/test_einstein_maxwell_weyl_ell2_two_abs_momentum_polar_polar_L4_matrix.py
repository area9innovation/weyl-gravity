from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


class PolarPolarL4MatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(
            (
                ROOT
                / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_polar_polar_L4_matrix.json"
            ).read_text()
        )

    def test_complete_polar_polar_basis_matrix(self) -> None:
        summary = self.value["matrix_summary"]
        self.assertEqual(summary["candidate_rows"], 12)
        self.assertEqual(summary["polar_input_basis_fixtures"], 20)
        self.assertEqual(summary["target_adjoint_coefficients"], 27)

    def test_every_stored_verdict_matches_its_cokernel_vector(self) -> None:
        fixtures = [
            fixture
            for row in self.value["candidate_rows"]
            for fixture in row["basis_fixtures"]
        ]
        self.assertEqual(len(fixtures), 20)
        for fixture in fixtures:
            has_witness = any(item is not None for item in fixture["pairing_intervals"])
            self.assertEqual(
                fixture["bounded_status"],
                "OBSTRUCTED" if has_witness else "OPEN",
            )

    def test_direct_calibration_is_retained(self) -> None:
        self.assertTrue(
            self.value["direct_calibration"]
            ["matches_direct_four_dimensional_source"]
        )

    def test_correction_classes_remain_distinct(self) -> None:
        verdict = self.value["second_order_verdict"]
        self.assertEqual(verdict["smooth_secular_status"], "OPEN")
        self.assertEqual(verdict["causal_retarded_status"], "NO_CERTIFIED_MAP")

    def test_workload_and_cone_are_fail_closed(self) -> None:
        progress = self.value["workload_progress"]
        self.assertEqual(progress["resolved_axisymmetric_L4_coefficients"], 54)
        self.assertEqual(progress["remaining_axisymmetric_L4_coefficients"], 54)
        self.assertEqual(progress["remaining_nonaxisymmetric_L1_L3_coefficients"], 56)
        self.assertFalse(progress["complete_two_fibre_tangent_cone_classified"])
        self.assertFalse(
            self.value["classification"]
            ["arbitrary_polar_linear_combinations_classified"]
        )


if __name__ == "__main__":
    unittest.main()
