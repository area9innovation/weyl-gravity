from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_axial_master_complex import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_axial_master_complex import (
    verify_certificate,
)


class EinsteinMaxwellAxialMasterComplexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_arbitrary_harmonic_tensor_remainders_vanish(self) -> None:
        tensor = self.payload["exact_fourier_equations"]
        self.assertEqual(tensor["all_symbolic_remainders"], "0")
        self.assertTrue(tensor["all_unlisted_rows_zero"])

    def test_exact_all_momentum_dispersion(self) -> None:
        theorem = self.payload["ell_ge_2_theorem"]
        self.assertEqual(theorem["branches"][0]["omega_squared"], "k_n^2+lambda+sqrt(2*lambda)")
        self.assertEqual(theorem["branches"][1]["omega_squared"], "k_n^2+lambda-sqrt(2*lambda)")
        self.assertTrue(theorem["tachyon_free"])

    def test_gauge_fixing_is_exception_aware(self) -> None:
        gauge = self.payload["gauge_fixing_and_reconstruction"]
        self.assertIn("fixes s uniquely", gauge["ell_ge_2"])
        self.assertIn("combined residual", gauge["ell_1"])

    def test_ell1_periodic_quotient_retains_only_global_twist(self) -> None:
        quotient = self.payload["ell1_quotient"]
        self.assertIn("periodic Fourier gauge parameter", quotient["periodic_nonzero_n"])
        self.assertIn("nonperiodic", quotient["n_zero"])
        self.assertEqual(quotient["physical_dispersive_branch"], "omega^2=k_n^2+4")

    def test_reduced_current_scope(self) -> None:
        pairing = self.payload["reduced_pairing"]
        self.assertEqual(pairing["symmetrizer"], [["lambda", "0"], ["0", "2"]])
        self.assertFalse(pairing["covariant_Einstein_Maxwell_symplectic_matching"])

    def test_remaining_gates_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["all_n_axial_master_complex_ell_ge_2"])
        self.assertFalse(classification["polar_master_complex"])
        self.assertFalse(classification["complete_fourth_order_adjoint_cokernel"])
        self.assertFalse(classification["full_harmonic_theorem"])

    def test_committed_certificate_matches_and_verifies(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
