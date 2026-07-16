from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_periodic_graviton_second_order import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    verify_certificate as verify_fast_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_periodic_graviton_second_order import (
    verify_certificate,
)


class EinsteinMaxwellPeriodicGravitonSecondOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_l2_mode_is_complete_linear_solution(self) -> None:
        mode = self.payload["first_order_mode"]
        self.assertEqual(mode["certified_branch"], "plus")
        self.assertTrue(all(value == "0" for row in mode["linearized_einstein_residual"] for value in row))
        self.assertTrue(all(value == "0" for value in mode["linearized_maxwell_residual"]))

    def test_mode_is_physical_and_fixed_charge(self) -> None:
        mode = self.payload["first_order_mode"]
        self.assertIn("not identically zero", mode["not_pure_gauge"])
        self.assertTrue(mode["electric_charge_variation"].endswith("=0"))
        self.assertTrue(mode["magnetic_charge_variation"].endswith("=0"))

    def test_chevreton_slice_is_nonzero(self) -> None:
        data = self.payload["chevreton_second_order_time_zero"]
        self.assertTrue(data["nonzero"])
        self.assertEqual(data["normalized_sphere_average_tt"], "-36*sqrt(3)/5 - 36/5")

    def test_fixed_charge_adjoint_obstruction(self) -> None:
        witness = self.payload["adjoint_cokernel_witness"]
        self.assertEqual(
            witness["conclusion"],
            "NO_SMOOTH_PERIODIC_SECOND_ORDER_CORRECTION_FOR_CERTIFIED_L2_BRANCH_AT_FIXED_CHARGES",
        )
        self.assertFalse(self.payload["classification"]["fixed_charge_second_order_extension_exists"])

    def test_claim_remains_one_branch(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["both_normal_branches_classified_at_second_order"])
        self.assertFalse(classification["all_helicity_two_harmonics_obstructed"])
        self.assertFalse(classification["general_nonlinear_closure_certified"])

    def test_committed_certificate_matches_and_verifies(self) -> None:
        verify_fast_certificate()
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
