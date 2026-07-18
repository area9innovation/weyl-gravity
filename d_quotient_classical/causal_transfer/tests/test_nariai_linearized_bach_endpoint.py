from __future__ import annotations

import copy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer.nariai_linearized_bach_endpoint import (
    SCHEMA,
    build,
)


class NariaiLinearizedBachEndpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()
        cls.schema = json.loads(SCHEMA.read_text())

    def test_tensor_and_noether_identities(self) -> None:
        checks = self.value["exact_checks"]
        for key in (
            "tensor_symmetry_defects",
            "tensor_trace_defect_entries",
            "tensor_divergence_defect_entries",
            "B_action_K_defect_entries",
        ):
            self.assertEqual(checks[key], 0)

    def test_parent_compression_identity(self) -> None:
        checks = self.value["exact_checks"]
        self.assertEqual(checks["corrected_parent_plus_2_B_action_defect_entries"], 0)
        self.assertTrue(checks["raw_defect_equals_minus_unique_Q"])

    def test_product_scaling(self) -> None:
        self.assertTrue(self.value["product_scaling_regression"]["exact_match"])
        self.assertEqual(
            self.value["product_scaling_regression"]["normalization"],
            "B_action=-2 B_standard",
        )

    def test_strict_schema(self) -> None:
        Draft202012Validator.check_schema(self.schema)
        Draft202012Validator(self.schema).validate(self.value)

    def test_source_manifest_pins_coefficient_generators(self) -> None:
        manifest = self.value["provenance"]["source_manifest"]
        for path in (
            "covariant_completion/curved_operator/adjoint_tractor_bgg_curved_pbw.py",
            "d_quotient_classical/causal_transfer/nariai_curvature_incidence_first_square.py",
            "d_quotient_classical/causal_transfer/nariai_first_differential_bgg_correction.py",
            "d_quotient_classical/causal_transfer/nariai_yang_mills_middle_compression.py",
        ):
            self.assertIn(path, manifest)

    def test_schema_rejects_causal_overpromotion(self) -> None:
        mutated = copy.deepcopy(self.value)
        mutated["flags"]["NARIAI_GREEN_HOMOTOPY"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)


if __name__ == "__main__":
    unittest.main()
