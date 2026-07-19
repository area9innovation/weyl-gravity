"""Tests for reduced Taub factorization."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_reduced_taub_factorization as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_reduced_taub_factorization import verify


class ReducedTaubFactorizationTests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), producer.build())
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["obstruction_dimension"], 5)
        self.assertEqual(result["factorization_rank"], 5)
        self.assertTrue(result["kernel_identity_exact"])

    def test_scope_stays_reduced_and_smooth(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        self.assertEqual(value["dependency_tags"], ["REDUCED-MODE"])
        self.assertTrue(value["classification"]["reduced_mode_obstruction_factorization_exact"])
        self.assertFalse(value["classification"]["support_local_relative_lift_constructed"])
        self.assertFalse(value["classification"]["serialized_all_mode_source_pair_matrix_computed"])
        self.assertFalse(value["classification"]["target_primal_obstruction_representatives_exported"])
        self.assertFalse(value["classification"]["bounded_correction_factorization_certified"])
        self.assertFalse(value["classification"]["causal_retarded_factorization_certified"])

    def test_forbidden_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        for key in ("serialized_all_mode_source_pair_matrix_computed", "target_primal_obstruction_representatives_exported", "support_local_relative_lift_constructed", "full_relative_q2_repaired", "bounded_correction_factorization_certified", "causal_retarded_factorization_certified", "arity_three_authorized", "observable_particle_or_quantum_claim"):
            mutant = deepcopy(json.loads(producer.OUTPUT.read_text()))
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
