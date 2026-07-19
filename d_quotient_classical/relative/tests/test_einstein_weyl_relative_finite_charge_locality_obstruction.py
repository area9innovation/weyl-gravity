"""Tests for the finite-charge support-local lift obstruction."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_finite_charge_locality_obstruction as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_finite_charge_locality_obstruction import verify


class RelativeFiniteChargeLocalityObstructionTests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        value = producer.build()
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), value)
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["charge_dimension"], 5)
        self.assertEqual(result["q2_witness"], "-108*(1 + sqrt(3))/5")
        self.assertFalse(result["direct_local_lift"])

    def test_current_cone_remains_open(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        self.assertEqual(value["minimal_admissible_enlargement"]["status"], "OPEN_COEFFICIENT_EXPORT")
        self.assertFalse(value["classification"]["local_noether_current_coefficients_exported"])
        self.assertFalse(value["classification"]["support_local_bv_koszul_extension_certified"])

    def test_false_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        for key in ("direct_five_charge_support_local_lift_exists", "local_noether_current_coefficients_exported", "support_local_bv_koszul_extension_certified", "direct_f2_repaired", "arity_three_authorized", "causal_observable_particle_or_quantum_claim"):
            mutant = deepcopy(json.loads(producer.OUTPUT.read_text()))
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
