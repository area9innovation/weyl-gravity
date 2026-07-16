from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_obstruction_bilinear import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_obstruction_bilinear import (
    verify_certificate,
)


class EinsteinMaxwellObstructionBilinearTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_declared_domain_is_not_promoted(self) -> None:
        self.assertEqual(self.payload["domain"]["name"], "H_fixture")
        self.assertIn("not_the_complete_domain", self.payload["domain"])
        self.assertFalse(self.payload["classification"]["complete_H0_linear_domain_classified"])

    def test_bilinear_matrix_is_symmetric_and_diagonal(self) -> None:
        matrix = self.payload["bilinear"]["matrix"]
        self.assertTrue(self.payload["bilinear"]["symmetric"])
        self.assertEqual([matrix[i][i] for i in range(4)], ["-2", "-1/2", "-16/3", "-12*(6 + 5*sqrt(3))/5"])
        self.assertTrue(all(matrix[i][j] == "0" for i in range(4) for j in range(4) if i != j))

    def test_l0_mixed_entry_was_computed_directly(self) -> None:
        mixed = self.payload["bilinear"]["radion_duality_direct_tensor_check"]
        self.assertEqual(mixed["combined_quadratic_source_tt"], "-(a_D**2 + 4*a_R**2)/2")
        self.assertEqual(mixed["twice_polarized_entry"], "0")

    def test_charge_fibre_changes_cokernel(self) -> None:
        fibres = self.payload["charge_fibres"]
        self.assertEqual(fibres["fixed_electric_fixed_magnetic"]["constant_lapse_cokernel"], "C_H survives")
        self.assertEqual(fibres["variable_magnetic"]["constant_lapse_cokernel"], "C_H is removed from the augmented cokernel")

    def test_taub_scope_is_relative(self) -> None:
        relation = self.payload["taub_relation"]
        self.assertEqual(relation["classification"], "RELATIVE_TAUB_MOMENT_MAP_COMPONENT")
        self.assertFalse(relation["covariant_symplectic_moment_map_identification_certified"])

    def test_full_harmonic_theorem_remains_open(self) -> None:
        self.assertFalse(self.payload["selection_rules"]["full_harmonic_coefficients_certified"])
        self.assertFalse(self.payload["classification"]["full_harmonic_obstruction_theorem"])

    def test_committed_certificate_matches_and_verifies(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
