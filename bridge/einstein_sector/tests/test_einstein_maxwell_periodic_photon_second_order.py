from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_periodic_photon_second_order import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_periodic_photon_second_order import (
    verify_certificate,
)


class EinsteinMaxwellPeriodicPhotonSecondOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_mode_is_nonzero_frequency_and_on_shell(self) -> None:
        mode = self.payload["first_order_mode"]
        self.assertEqual(mode["physical_frequency_squared"], 4)
        self.assertTrue(all(value == "0" for row in mode["linearized_einstein_residual"] for value in row))
        self.assertTrue(all(value == "0" for value in mode["linearized_maxwell_residual"]))

    def test_first_order_charges_vanish(self) -> None:
        mode = self.payload["first_order_mode"]
        self.assertTrue(mode["electric_charge_variation"].endswith("=0"))
        self.assertTrue(mode["magnetic_charge_variation"].endswith("=0"))

    def test_chevreton_tensor_is_nonzero(self) -> None:
        chevreton = self.payload["chevreton_second_order"]
        self.assertTrue(chevreton["nonzero"])
        self.assertEqual(chevreton["normalized_sphere_average_tt"], "-8/3")

    def test_fixed_charge_adjoint_obstruction(self) -> None:
        witness = self.payload["adjoint_cokernel_witness"]
        self.assertEqual(witness["normalized_source_pairing"], "-16/3")
        self.assertEqual(
            witness["conclusion"],
            "NO_SMOOTH_PERIODIC_SECOND_ORDER_CORRECTION_AT_FIXED_ELECTRIC_AND_MAGNETIC_CHARGES",
        )
        self.assertFalse(self.payload["classification"]["fixed_charge_second_order_extension_exists"])

    def test_claim_boundary_remains_scoped(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["general_photon_harmonic_no_go_certified"])
        self.assertFalse(classification["periodic_helicity_two_result_certified"])
        self.assertFalse(classification["general_nonlinear_closure_certified"])

    def test_committed_certificate_matches_and_verifies(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
