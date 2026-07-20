"""Tests for the streamed five-current second-jet export."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_full_five_current_second_jet_export as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_full_five_current_second_jet_export import verify


class FullFiveCurrentSecondJetExportTests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        certificate, manifest, _ = producer.build_outputs()
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), certificate)
        self.assertEqual(json.loads(producer.MANIFEST.read_text()), manifest)
        self.assertEqual(producer.REPORT.read_text(), producer._report(certificate))

    def test_independent_chunkwise_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["chunks"], 20)
        self.assertTrue(result["independent_second_jet_replay"])
        self.assertGreater(result["v1_terms_replayed"], 30000)

    def test_forbidden_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        value = json.loads(producer.OUTPUT.read_text())
        for key in (
            "support_local_chain_map_A_constructed",
            "order_one_top_descent_solved",
            "relative_q2_repaired",
            "causal_observable_particle_or_quantum_claim",
        ):
            mutant = deepcopy(value)
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
