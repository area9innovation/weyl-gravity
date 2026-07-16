from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_reduced_action_hessian import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)


class AxialReducedActionHessianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_reduced_hessian_triangle(self) -> None:
        self.assertTrue(self.payload["reconstruction"]["mixed_variation_equals_K"])
        self.assertTrue(self.payload["normalization_triangle"]["equation_operator_equals_reduced_action_Hessian"])
        self.assertTrue(self.payload["normalization_triangle"]["Green_current_equals_direct_integrated_four_dimensional_Lee_Wald_current"])

    def test_direct_density_claim_stays_open(self) -> None:
        self.assertFalse(self.payload["normalization_triangle"]["literal_direct_four_dimensional_action_density_second_expansion"])


if __name__ == "__main__":
    unittest.main()
