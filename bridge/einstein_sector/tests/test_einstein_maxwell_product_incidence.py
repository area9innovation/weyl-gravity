from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_product_incidence import (
    ROOT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_product_incidence import (
    verify_certificate,
)


class EinsteinMaxwellProductIncidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            self.payload["schema"], schema["properties"]["schema"]["const"]
        )
        self.assertEqual(
            self.payload["result_id"], schema["properties"]["result_id"]["const"]
        )
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_exact_same_field_incidence(self) -> None:
        theorem = self.payload["common_incidence_theorem"]
        self.assertEqual(
            theorem["coupling_curvature_incidence"],
            "alpha_B*kappa*(k_1+k_2)=3",
        )
        self.assertEqual(theorem["einstein_maxwell_equation"], "PASS componentwise")
        self.assertEqual(
            theorem["pure_weyl_maxwell_equation"], "PASS componentwise"
        )
        self.assertTrue(theorem["same_metric"])
        self.assertTrue(theorem["same_maxwell_field"])

    def test_flat_critical_branch_is_positive_and_spatially_compactifiable(self) -> None:
        branch = self.payload["flat_critical_branch"]
        self.assertEqual(branch["local_geometry"], "R^(1,1) x S^2")
        self.assertTrue(branch["positive_energy_for_positive_couplings"])
        self.assertTrue(branch["smooth_spatial_quotient"])
        self.assertEqual(branch["compact_cauchy_topology"], "S^1 x S^2")
        self.assertFalse(branch["relational_matter_clock"])
        self.assertFalse(branch["asymptotically_flat"])

    def test_degenerate_endpoints_are_not_misclassified(self) -> None:
        branches = self.payload["degenerate_branches"]
        self.assertIn("flux-free", branches["k_1_equals_k_2"]["classification"])
        self.assertIn(
            "no same-field incidence",
            branches[
                "k_1_plus_k_2_equals_zero_with_unequal_curvatures"
            ]["classification"],
        )

    def test_rational_fixture_and_u1_refinement(self) -> None:
        fixture = self.payload["rational_fixture"]
        self.assertEqual(fixture["parameters"]["alpha_B"], "3")
        self.assertEqual(fixture["both_metric_equations"], "PASS")
        self.assertEqual(
            self.payload["u1_flux_quantization"]["flat_branch_discrete_coupling"],
            "alpha_B=3*N**2/(4*q_min**2)",
        )

    def test_claim_boundary_fails_closed(self) -> None:
        classification = self.payload["classification"]
        flags = self.payload["claim_flags"]
        self.assertTrue(
            classification[
                "exact_common_einstein_maxwell_weyl_maxwell_background_exists"
            ]
        )
        self.assertFalse(classification["linearized_tangent_complex_map_constructed"])
        self.assertFalse(classification["theories_proved_equivalent"])
        self.assertFalse(flags["relational_clock_certified"])
        self.assertFalse(flags["lorentzian_green_complex_certified"])
        self.assertFalse(flags["scattering_sector_certified"])

    def test_committed_certificate_matches_and_verifies_independently(self) -> None:
        certificate = (
            ROOT / "bridge/certificates/einstein_maxwell_product_incidence.json"
        )
        if not certificate.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(
            json.loads(certificate.read_text(encoding="utf-8")), self.payload
        )
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
