from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_harmonic_adjoint_blocks import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_harmonic_adjoint_blocks import (
    verify_certificate,
)


class EinsteinMaxwellHarmonicAdjointBlockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_all_ell_identity_and_new_tensor_regressions(self) -> None:
        tower = self.payload["axial_n0_tower"]
        self.assertEqual(tower["all_ell_identity_proof"]["Einstein_angular_remainder_reduces_to"], "0")
        self.assertEqual(tower["all_ell_identity_proof"]["Maxwell_angular_remainder_reduces_to"], "0")
        self.assertEqual(
            [(row["ell"], row["lambda"]) for row in tower["new_direct_tensor_regressions"]],
            [(3, 12), (4, 20)],
        )

    def test_exact_branch_formula(self) -> None:
        spectral = self.payload["axial_n0_tower"]["spectral_data"]
        self.assertEqual(spectral["branches"]["plus"]["omega_squared"], "lambda+sqrt(2*lambda)")
        self.assertEqual(spectral["branches"]["minus"]["omega_squared"], "lambda-sqrt(2*lambda)")
        self.assertEqual(spectral["branch_wronskian_norm"], "2*lambda")

    def test_ell1_zero_mode_is_globally_exceptional(self) -> None:
        zero = self.payload["axial_n0_tower"]["physical_branch_classification"]["ell_1_minus"]
        self.assertEqual(zero["S1_monodromy"]["Delta_xi_phi"], "H_0*L")
        self.assertIn("NOT_GENERATED_BY_A_SMOOTH_PERIODIC", zero["global_classification"])

    def test_adjoint_target_inventory(self) -> None:
        targets = self.payload["universal_adjoint_targets"]
        self.assertEqual(targets["metric_KID_dimension"], 5)
        self.assertEqual(targets["metric_KID_basis"][:2], ["H=partial_t", "P_x=partial_x"])
        self.assertFalse(targets["complete_full_weyl_maxwell_adjoint_cokernel"])

    def test_fail_closed_decision_protocol(self) -> None:
        protocol = self.payload["decision_protocol"]
        self.assertEqual(protocol["zero_constant_lapse_only"], "INCONCLUSIVE")
        self.assertIn("explicit Phi^(2)", protocol["extension_certificate"])

    def test_remaining_blocks_are_not_promoted(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["declared_axial_n0_tower_all_ell_m"])
        self.assertFalse(classification["complete_axial_n0_gauge_quotient"])
        self.assertFalse(classification["complete_all_parity_momentum_blocks"])
        self.assertFalse(classification["complete_full_adjoint_cokernel"])

    def test_committed_certificate_matches_and_verifies(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
