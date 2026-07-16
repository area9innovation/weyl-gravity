from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_polar_master_preflight import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_polar_master_preflight import (
    verify_certificate,
)


class EinsteinMaxwellPolarMasterPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_volume_density_correction_is_explicit(self) -> None:
        correction = self.payload["volume_density_correction"]
        self.assertIn("perturbed determinant", correction["correct_operator"])
        self.assertIn("(A-C)/2+K", correction["consequence"])

    def test_generic_matrix_and_constraint_reduction(self) -> None:
        reduction = self.payload["algebraic_master_reduction"]
        self.assertEqual(len(reduction["coefficient_matrix"]), 8)
        self.assertTrue(all(len(row) == 5 for row in reduction["coefficient_matrix"]))
        self.assertEqual(reduction["constraints"][0], "A=C")
        self.assertEqual(reduction["reconstruction"][0], "R=K-2U")

    def test_polar_axial_isospectrality(self) -> None:
        reduction = self.payload["algebraic_master_reduction"]
        self.assertEqual(reduction["master_matrix"], [["lambda", "-2*lambda"], ["-1", "lambda"]])
        self.assertEqual(reduction["dispersion"], "omega^2=k_n^2+lambda+/-sqrt(2*lambda)")
        self.assertIn("certified axial eigenvalues", self.payload["isospectral_relation"])

    def test_exact_l2_plus_tensor_fixture(self) -> None:
        fixture = self.payload["exact_tensor_fixture"]
        self.assertEqual(fixture["ell"], 2)
        self.assertEqual(fixture["branch"], "plus")
        self.assertEqual(fixture["Einstein_residual"], "0")
        self.assertEqual(fixture["Maxwell_density_residual"], "0")
        self.assertIn("0<theta<pi", fixture["chart_convention"])

    def test_reduced_current_scope(self) -> None:
        pairing = self.payload["reduced_pairing"]
        self.assertEqual(pairing["symmetrizer"], "diag(1,2lambda)")
        self.assertFalse(pairing["covariant_symplectic_matching"])

    def test_exceptional_and_promotion_gates_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["generic_polar_matrix"])
        self.assertFalse(classification["all_ell_arbitrary_lambda_tensor_derivation"])
        self.assertFalse(classification["ell0_ell1_complete"])
        self.assertFalse(classification["complete_fourth_order_adjoint"])
        self.assertFalse(classification["full_polar_master_theorem"])

    def test_committed_certificate_matches_and_verifies(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
