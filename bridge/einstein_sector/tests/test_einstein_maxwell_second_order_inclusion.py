from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_second_order_inclusion import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_second_order_inclusion import (
    verify_certificate,
)


class EinsteinMaxwellSecondOrderInclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(
            self.payload["result_id"], schema["properties"]["result_id"]["const"]
        )
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_constant_radion_has_fixed_flux_adjoint_obstruction(self) -> None:
        fixture = self.payload["certified_constant_radion"]
        self.assertEqual(fixture["affine_quadratic_weyl_maxwell_source"][0][0], "-2")
        witness = fixture["compact_fixed_flux_adjoint_witness"]
        self.assertTrue(witness["nonzero_for_L_positive"])
        self.assertEqual(
            witness["conclusion"],
            "NO_PERIODIC_SECOND_ORDER_CORRECTION_AT_FIXED_MAGNETIC_FLUX",
        )

    def test_constant_radion_extends_if_flux_may_shift(self) -> None:
        extension = self.payload["certified_constant_radion"]["charge_relaxed_extension"]
        self.assertEqual(extension["magnetic_flux_shift"], "P(epsilon)=1-2*epsilon^2")
        self.assertTrue(
            all(value == "0" for row in extension["corrected_residual"] for value in row)
        )

    def test_maxwell_duality_tangent_is_charge_sector_dependent(self) -> None:
        fixture = self.payload["maxwell_duality_tangent"]
        self.assertEqual(fixture["affine_fixed_magnetic_flux_source"][0][0], "-1/2")
        self.assertEqual(
            fixture["charge_relaxed_extension"]["second_order_correction"],
            "f2=-(1/2)*Fbar",
        )
        self.assertIn("cos(epsilon)", fixture["charge_relaxed_extension"]["all_order_family"])

    def test_nonzero_chevreton_radiative_source_is_removable(self) -> None:
        fixture = self.payload["null_radiative_tangent"]
        self.assertEqual(fixture["convention_adjusted_C_Ch_second_order"][0][0], "4")
        self.assertEqual(fixture["convention_adjusted_C_Ch_second_order"][0][1], "-4")
        self.assertEqual(
            fixture["explicit_extension"]["status"],
            "EXPLICIT_SECOND_ORDER_EXTENSION_WITH_NONZERO_CHEVRETON_DEFECT",
        )
        self.assertTrue(
            all(
                value == "0"
                for row in fixture["explicit_extension"]["corrected_residual"]
                for value in row
            )
        )

    def test_adjoint_reduction_covers_arbitrary_periodic_corrections(self) -> None:
        reduction = self.payload["adjoint_cokernel_reduction"]
        self.assertIn("averaging", reduction)
        self.assertIn("arbitrary smooth periodic corrections", reduction["scope"])
        self.assertEqual(reduction["fixed_flux_condition"], "p=0")

    def test_general_claims_remain_open(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["general_nonlinear_einstein_sector_closure_certified"])
        self.assertFalse(classification["general_second_order_no_go_certified"])
        self.assertFalse(
            classification["nonzero_chevreton_defect_is_by_itself_an_obstruction"]
        )
        self.assertEqual(self.payload["next_gate"]["status"], "OPEN")

    def test_committed_certificate_matches_and_verifies_independently(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
