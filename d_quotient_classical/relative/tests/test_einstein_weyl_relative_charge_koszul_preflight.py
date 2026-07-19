"""Tests for the relative charge/Koszul receiver preflight."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_charge_koszul_preflight as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_charge_koszul_preflight import verify


class RelativeChargeKoszulPreflightTests(unittest.TestCase):
    def test_generated_outputs_are_current(self) -> None:
        value = producer.build()
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), value)
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["endpoint_rank"], 6)
        self.assertEqual(result["charge_fibre_rank"], 5)
        self.assertEqual(result["koszul_monomials_checked"], 32)
        self.assertTrue(result["quadratic_origin_and_linearization_zero"])

    def test_category_boundary(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        self.assertEqual(value["dependency_tags"], ["REDUCED-MODE"])
        self.assertEqual(value["charge_fibre"]["dimension"], 5)
        self.assertEqual(
            value["charge_fibre"]["constant_u1_endpoint"]["disposition"],
            "REDUCIBILITY_NOT_A_SIXTH_TAUB_CHARGE",
        )
        self.assertFalse(value["classification"]["relative_f2_repaired"])
        self.assertFalse(value["classification"]["arity_three_authorized"])

    def test_false_promotions_are_schema_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        for key in (
            "constant_u1_is_sixth_taub_charge",
            "plain_linear_taub_zero_subcomplex_valid",
            "full_offshell_charge_map_certified",
            "relative_f2_repaired",
            "arity_three_authorized",
            "causal_observable_particle_or_quantum_claim",
        ):
            mutant = deepcopy(json.loads(producer.OUTPUT.read_text()))
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
