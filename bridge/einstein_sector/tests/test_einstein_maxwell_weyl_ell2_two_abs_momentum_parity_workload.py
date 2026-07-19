from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class TwoAbsMomentumParityWorkloadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads((ROOT / "bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_parity_workload.json").read_text())

    def test_all_candidates_are_typed_without_silent_deletion(self) -> None:
        self.assertEqual(len(self.value["source_workload"]["rows"]), 21)
        self.assertEqual(self.value["selection_theorem"]["candidate_rows_eliminated"], 0)
        self.assertEqual(self.value["selection_theorem"]["allowed_parity_channels"], 84)

    def test_workload_counts_internal_multiplicity(self) -> None:
        workload = self.value["source_workload"]
        self.assertEqual(workload["reduced_scalar_source_coefficients"], 164)
        self.assertEqual(workload["target_axial_coefficients"], 82)
        self.assertEqual(workload["target_polar_coefficients"], 82)

    def test_odd_outputs_require_nonaxisymmetric_fixture(self) -> None:
        workload = self.value["source_workload"]
        self.assertEqual(workload["odd_L_coefficients_requiring_nonaxisymmetric_fixture"], 56)
        for row in workload["rows"]:
            if row["output_ell"] % 2:
                self.assertTrue(all(not channel["axisymmetric_fixture_available"] for channel in row["parity_channels"]))

    def test_sources_and_cone_remain_open(self) -> None:
        classification = self.value["classification"]
        self.assertFalse(classification["projected_source_coefficients_computed"])
        self.assertFalse(classification["complete_two_fibre_tangent_cone_classified"])


if __name__ == "__main__":
    unittest.main()
