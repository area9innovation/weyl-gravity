from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_chevreton_tangent import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_chevreton_tangent import (
    verify_certificate,
)


class EinsteinMaxwellChevretonTangentTests(unittest.TestCase):
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

    def test_factorization_and_tuning_close_the_linear_defect(self) -> None:
        factorization = self.payload["on_shell_factorization"]
        self.assertIn("quadratic in nabla F", factorization["structural_property"])
        self.assertEqual(factorization["linearized_consequence"].split()[0:3], ["delta", "C_Ch=0", "for"])
        self.assertEqual(self.payload["tuning_deduction"]["symbolic_check"], "1")

    def test_complete_on_shell_solution_tangent_inclusion(self) -> None:
        theorem = self.payload["theorem"]
        self.assertTrue(theorem["includes_curvature_lower_order_terms"])
        self.assertTrue(theorem["includes_background_flux_mixing_on_shell"])
        self.assertEqual(theorem["field_map"], "identity on (h_mn,a_m)")
        self.assertTrue(theorem["not_an_off_shell_chain_map"])

    def test_radion_fixture_satisfies_both_complete_linearized_systems(self) -> None:
        fixture = self.payload["direct_radion_fixture"]
        self.assertEqual(fixture["full_lower_order_coordinate_check"], "PASS")
        self.assertTrue(
            all(value == "0" for row in fixture["linearized_einstein_residual"] for value in row)
        )
        self.assertTrue(
            all(value == "0" for row in fixture["linearized_weyl_residual"] for value in row)
        )
        self.assertTrue(all(value == "0" for value in fixture["linearized_maxwell_residual"]))

    def test_first_possible_chevreton_defect_is_quadratic(self) -> None:
        onset = self.payload["quadratic_onset"]
        self.assertEqual(onset["first_variation"], "0")
        self.assertNotEqual(onset["second_variation"], "0")

    def test_claim_boundary_keeps_distinct_gates_open(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["full_lower_order_on_shell_linear_tangent_inclusion"])
        self.assertTrue(
            classification[
                "ordinary_einstein_graviton_and_photon_tangents_survive_before_quotient"
            ]
        )
        self.assertFalse(classification["off_shell_curved_minimal_bv_chain_map_constructed"])
        self.assertFalse(classification["quotient_observable_injection_constructed"])
        self.assertFalse(classification["covariant_presymplectic_map_constructed"])
        self.assertFalse(classification["nonlinear_einstein_maxwell_sector_closure_certified"])
        self.assertEqual(self.payload["next_gate"]["status"], "OPEN")

    def test_committed_certificate_matches_and_verifies_independently(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
