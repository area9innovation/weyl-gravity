"""Tests for the relative Hessian second-current coefficient input."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_hessian_second_current_input as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_hessian_second_current_input import verify


class RelativeHessianSecondCurrentInputTests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        payload = json.loads(producer.PAYLOAD.read_text())
        certificate = producer.build_certificate(payload)
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), certificate)
        self.assertEqual(producer.REPORT.read_text(), producer._report(certificate))

    def test_independent_fast_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["second_current_depth_complete"])
        self.assertGreater(result["raw_target_fifth_jets"], 0)
        self.assertGreater(result["raw_source_third_jets"], 0)
        self.assertEqual(result["relative_fifth_jets"], 0)
        self.assertEqual(result["relative_source_order_third_jets"], 0)

    def test_forbidden_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        value = json.loads(producer.OUTPUT.read_text())
        for key in (
            "five_current_second_jet_exported",
            "support_local_chain_map_A_constructed",
            "relative_q2_repaired",
            "causal_observable_particle_or_quantum_claim",
        ):
            mutant = deepcopy(value)
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
