from __future__ import annotations

import json
import unittest

from bridge.einstein_sector.einstein_maxwell_product_tangent_preflight import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_product_tangent_preflight import (
    verify_certificate,
)


class EinsteinMaxwellProductTangentPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_contract(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["schema"], schema["properties"]["schema"]["const"])
        self.assertEqual(self.payload["result_id"], schema["properties"]["result_id"]["const"])
        self.assertEqual(set(self.payload), set(schema["required"]))

    def test_both_minimal_layouts_include_maxwell(self) -> None:
        layouts = self.payload["minimal_complex_layouts"]
        self.assertEqual(layouts["einstein_maxwell"]["dimensions"], [5, 14, 14, 5])
        self.assertEqual(layouts["weyl_maxwell"]["dimensions"], [6, 14, 14, 6])
        self.assertIn("lambda_U1", layouts["einstein_maxwell"]["ghosts"])
        self.assertIn("sigma_Weyl", layouts["weyl_maxwell"]["ghosts"])

    def test_all_principal_chain_squares_pass(self) -> None:
        chain = self.payload["principal_chain_map"]
        for key in (
            "ghost_field_square",
            "field_equation_square",
            "equation_identity_square",
            "einstein_nilpotency_rows",
            "weyl_nilpotency_rows",
        ):
            self.assertEqual(chain[key], "PASS")

    def test_noncharacteristic_complexes_are_exact(self) -> None:
        fixture = self.payload["symbol_cohomology"]["noncharacteristic_fixture"]
        self.assertEqual(
            fixture["cohomology_dimensions"],
            {
                "einstein_field": 0,
                "einstein_equation": 0,
                "weyl_field": 0,
                "weyl_equation": 0,
            },
        )

    def test_null_einstein_classes_inject_with_two_class_cokernel(self) -> None:
        fixture = self.payload["symbol_cohomology"]["null_fixture"]
        self.assertEqual(
            fixture["block_field_cohomology"],
            {
                "einstein_metric": 2,
                "photon_in_einstein_maxwell": 2,
                "weyl_metric_simple_symbol": 4,
                "photon_in_weyl_maxwell": 2,
            },
        )
        induced = fixture["induced_field_cohomology_map"]
        self.assertTrue(induced["induced_map_injective"])
        self.assertEqual(induced["source_dimension"], 4)
        self.assertEqual(induced["target_dimension"], 6)
        self.assertEqual(induced["cokernel_dimension"], 2)

    def test_curved_and_generalized_mode_claims_remain_open(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["full_curved_tangent_chain_map_constructed"])
        self.assertFalse(classification["covariant_presymplectic_map_constructed"])
        self.assertFalse(classification["helicity_assignment_on_product_background_completed"])
        self.assertFalse(classification["generalized_fourth_order_modes_classified"])
        self.assertEqual(self.payload["curved_completion_gate"]["status"], "OPEN")

    def test_committed_certificate_matches_and_verifies_independently(self) -> None:
        if not DEFAULT_OUTPUT.exists():
            self.skipTest("generated certificate has not been written yet")
        self.assertEqual(
            json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload
        )
        verify_certificate()


if __name__ == "__main__":
    unittest.main()
