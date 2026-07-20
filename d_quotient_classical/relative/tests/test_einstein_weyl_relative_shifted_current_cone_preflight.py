"""Tests for the shifted current-cone preflight."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_shifted_current_cone_preflight as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_shifted_current_cone_preflight import verify


class ShiftedCurrentConePreflightTests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), producer.build())
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_rank_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["primal_ranks"], [5, 20, 30, 20, 5])
        self.assertEqual(result["shifted_base_ranks"], [5, 25, 50, 48, 24, 6])
        self.assertEqual(result["shifted_completed_ranks"], [5, 25, 56, 72, 72, 56, 25, 5])
        self.assertNotEqual(result["shifted_completed_ranks"], result["old_completed_ranks"])

    def test_exact_scope_stays_preflight(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        self.assertEqual(value["dependency_tags"], ["LOCAL-ALGEBRAIC"])
        self.assertTrue(value["classification"]["required_lift_typed"])
        self.assertTrue(value["classification"]["shifted_mapping_cone_required"])
        self.assertFalse(value["classification"]["support_local_chain_map_A_constructed"])
        self.assertFalse(value["classification"]["top_descent_solved"])
        self.assertFalse(value["classification"]["relative_q2_repaired"])

    def test_forbidden_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        value = json.loads(producer.OUTPUT.read_text())
        for key in (
            "existing_316_direct_sum_grading_sufficient",
            "support_local_chain_map_A_constructed",
            "top_descent_solved",
            "relative_q2_repaired",
            "causal_observable_particle_or_quantum_claim",
        ):
            mutant = deepcopy(value)
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
