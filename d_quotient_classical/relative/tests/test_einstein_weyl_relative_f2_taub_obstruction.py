"""Scoped tests for the compact-product relative f2 Taub obstruction."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_f2_taub_obstruction as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_f2_taub_obstruction import verify


class RelativeF2TaubObstructionTests(unittest.TestCase):
    def test_generated_outputs_are_current(self) -> None:
        value = producer.build()
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), value)
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(
            result["nonzero_delta2_rows"],
            ["g_00_star", "g_11_star", "g_22_star", "g_33_star"],
        )
        self.assertEqual(result["relative_half_delta2_pairing"], "-54*(1 + sqrt(3))/5")

    def test_claim_is_fail_closed(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        flags = value["classification"]
        self.assertFalse(flags["frozen_unary_full_domain_f2_exists"])
        self.assertFalse(flags["arity_three_direct_morphism_authorized"])
        self.assertFalse(flags["taub_zero_restricted_source_obstructed"])
        self.assertFalse(flags["relative_cofiber_or_mapping_cone_obstructed"])
        self.assertFalse(flags["causal_or_quantum_claim"])

    def test_false_promotions_are_schema_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        for key in (
            "frozen_unary_full_domain_f2_exists",
            "arity_three_direct_morphism_authorized",
            "taub_zero_restricted_source_obstructed",
            "causal_or_quantum_claim",
        ):
            mutant = deepcopy(json.loads(producer.OUTPUT.read_text()))
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
