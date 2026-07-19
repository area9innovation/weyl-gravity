"""Tests for the relative Hessian Green-current cone."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_hessian_green_current_cone as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_hessian_green_current_cone import verify


class RelativeHessianGreenCurrentConeTests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        value, generated = producer.build()
        recorded = json.loads(producer.OUTPUT.read_text())
        value["provenance"]["source_manifest"] = recorded["provenance"]["source_manifest"]
        self.assertEqual(recorded, value)
        self.assertEqual(json.loads(producer.GENERATED.read_text()), generated)

    def test_independent_telescoping_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["current_terms"], 3704)
        self.assertEqual(result["divergence_defects"], 0)
        self.assertEqual(result["formal_adjoint_defects"], 0)

    def test_downstream_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        value = json.loads(producer.OUTPUT.read_text())
        for key in (
            "five_stabilizer_noether_precomposition_certified",
            "lee_wald_improvement_comparison_certified",
            "cyclic_dual_bv_rows_certified",
            "slice_integral_matches_complete_five_charge_q2",
            "direct_f2_repaired",
            "arity_three_authorized",
            "causal_observable_particle_or_quantum_claim",
        ):
            mutant = deepcopy(value)
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
