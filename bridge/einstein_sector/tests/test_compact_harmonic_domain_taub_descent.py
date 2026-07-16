from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.compact_harmonic_domain_taub_descent import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_compact_harmonic_domain_taub_descent import (
    verify_certificate,
)


class CompactHarmonicDomainTaubDescentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_fixed_bundle_forbids_magnetic_lift(self) -> None:
        fibres = self.payload["topology_and_charge_fibres"]
        self.assertFalse(fibres["fixed_compact_u1_bundle"]["allowed_magnetic_lift"])
        self.assertEqual(fibres["exact_flux_check"]["fixture"]["chern_family"], "2*epsilon**2*p + 2")
        self.assertEqual(fibres["exact_flux_check"]["fixture"]["fixed_bundle_consequence"], "p=0")

    def test_continuous_flux_is_a_different_phase_space(self) -> None:
        enlarged = self.payload["topology_and_charge_fibres"]["enlarged_continuous_flux_theory"]
        self.assertTrue(enlarged["allowed_magnetic_lift"])
        self.assertTrue(enlarged["not_the_same_phase_space"])

    def test_electric_only_variation_does_not_lift_constant_lapse(self) -> None:
        stress = self.payload["topology_and_charge_fibres"]["linear_stress_check"]
        self.assertEqual(stress["linear_variation"], "E*dE + P*dP")
        self.assertEqual(stress["at_E_zero_P_one"], "dP")

    def test_gauge_descent_and_slice_conservation(self) -> None:
        self.assertEqual(
            self.payload["noether_gauge_descent"]["status"],
            "FORMAL_ACTION_NOETHER_DESCENT_CERTIFIED",
        )
        self.assertEqual(self.payload["slice_conservation"]["exact_symbolic_contraction"], "0")
        self.assertTrue(self.payload["classification"]["cauchy_slice_independence"])

    def test_harmonic_domain_stays_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["complete_linear_cohomology_computed"])
        self.assertFalse(classification["complete_adjoint_cokernel_computed"])
        self.assertFalse(classification["full_harmonic_coefficients_computed"])

    def test_fixture_bilinear_is_now_a_fixed_bundle_taub_form(self) -> None:
        theorem = self.payload["taub_theorem"]
        self.assertIn("fixed compact U(1) bundle", theorem["statement"])
        self.assertFalse(theorem["full_covariant_symplectic_moment_map_equality"])

    def test_committed_certificate_matches_and_verifies(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
