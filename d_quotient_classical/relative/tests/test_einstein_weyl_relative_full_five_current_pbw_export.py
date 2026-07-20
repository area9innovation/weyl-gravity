"""Tests for the portable full five-current PBW export."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_full_five_current_pbw_export as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_full_five_current_pbw_export import verify


class FullFiveCurrentPBWExportTests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        certificate, payload = producer.build()
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), certificate)
        self.assertEqual(json.loads(producer.PAYLOAD.read_text()), payload)
        self.assertEqual(producer.REPORT.read_text(), producer._report(certificate))

    def test_independent_coefficient_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["canonical_terms"], 30494)
        self.assertEqual(result["expanded_terms"], 60890)
        self.assertEqual(result["coefficient_profiles"], 239)
        self.assertTrue(result["independent_coefficient_replay"])

    def test_payload_is_typed_and_fail_closed(self) -> None:
        certificate = json.loads(producer.OUTPUT.read_text())
        payload = json.loads(producer.PAYLOAD.read_text())
        self.assertEqual(len(payload["field_order"]), 14)
        self.assertEqual(len(payload["output_rows"]), 20)
        self.assertEqual(payload["input_exchange_symmetry"], "symmetric_expand_off_diagonal")
        self.assertEqual(payload["maximum_coefficient_jet_order"], 1)
        self.assertFalse(certificate["classification"]["support_local_chain_map_A_constructed"])
        self.assertFalse(certificate["classification"]["top_descent_solved"])

    def test_forbidden_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        value = json.loads(producer.OUTPUT.read_text())
        for key in (
            "support_local_chain_map_A_constructed", "top_descent_solved",
            "relative_q2_repaired", "causal_observable_particle_or_quantum_claim",
        ):
            mutant = deepcopy(value)
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
