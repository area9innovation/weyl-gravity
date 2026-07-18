from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_weyl_relative_linear_triangle_v1 import (
    COMPONENT_SCHEMA,
    COMPONENTS,
    OUTPUT,
    TRIANGLE_SCHEMA,
    build_components,
    build_triangle,
    verify_outputs,
)
from bridge.einstein_sector.verify_einstein_weyl_relative_linear_triangle_v1 import (
    verify_certificate as verify_independently,
)


class EinsteinWeylRelativeLinearTriangleTests(unittest.TestCase):
    def test_generated_artifacts_are_current(self) -> None:
        verify_outputs()

    def test_both_strict_schemas(self) -> None:
        components = build_components()
        triangle = build_triangle(components)
        component_schema = json.loads(COMPONENT_SCHEMA.read_text(encoding="utf-8"))
        triangle_schema = json.loads(TRIANGLE_SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(component_schema)
        Draft202012Validator.check_schema(triangle_schema)
        Draft202012Validator(component_schema).validate(components)
        Draft202012Validator(triangle_schema).validate(triangle)

    def test_independent_consumer(self) -> None:
        verify_independently()

    def test_endpoint_and_noncyclic_scope(self) -> None:
        components = json.loads(COMPONENTS.read_text(encoding="utf-8"))
        triangle = json.loads(OUTPUT.read_text(encoding="utf-8"))
        endpoints = components["global_endpoints"]
        self.assertEqual(endpoints["source_dimension"], 6)
        self.assertEqual(endpoints["target_dimension"], 6)
        self.assertEqual(endpoints["cone_cohomology_dimension"], 0)
        self.assertEqual(endpoints["fixed_chern_class"], "N=2")
        self.assertEqual(triangle["pairing_disposition"]["triangle_kind"], "NONCYCLIC_THREE_FORM")
        self.assertFalse(triangle["pairing_disposition"]["standard_pairing_cyclic_map_exists"])

    def test_fail_closed_theorem_boundary(self) -> None:
        components = build_components()
        classification = components["classification"]
        self.assertTrue(classification["off_shell_all_row_chain_map"])
        self.assertTrue(classification["support_local_mapping_cofiber"])
        self.assertTrue(classification["global_endpoints_included"])
        self.assertTrue(classification["three_action_derived_forms_exported"])
        self.assertFalse(classification["standard_pairing_cyclic_map"])
        self.assertFalse(classification["causal_nonlinear_observational_or_quantum_claim"])


if __name__ == "__main__":
    unittest.main()
