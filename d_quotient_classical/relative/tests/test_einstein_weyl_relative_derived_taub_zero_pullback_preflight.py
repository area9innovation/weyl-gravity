"""Tests for the derived Taub-zero pullback preflight."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_derived_taub_zero_pullback_preflight as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_derived_taub_zero_pullback_preflight import verify


class DerivedTaubZeroPullbackPreflightTests(unittest.TestCase):
    def test_generated_outputs_are_current(self) -> None:
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), producer.build())
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["moment_constant_and_linear_terms_zero"])
        self.assertTrue(result["unary_tangent_unchanged"])
        self.assertEqual(result["current_interface_rows"], 188)
        self.assertEqual(result["charge_generators"], 5)

    def test_factorization_gate_remains_open(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        self.assertFalse(value["relative_morphism_gate"]["factorization_matrix_computed"])
        self.assertFalse(value["classification"]["relative_q2_on_derived_pullback_certified"])
        self.assertFalse(value["classification"]["factorization_obstructed"])
        self.assertIn("ker(mu_rel)", value["relative_morphism_gate"]["equivalent_kernel_condition"])

    def test_false_promotions_are_schema_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        for key in ("linear_tangent_must_be_restricted", "unary_cross_incidence_required_by_taub_zero_condition", "relative_q2_on_derived_pullback_certified", "factorization_obstructed", "causal_or_quantum_claim"):
            mutant = deepcopy(json.loads(producer.OUTPUT.read_text()))
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
