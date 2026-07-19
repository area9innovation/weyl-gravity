"""Tests for the standard-radiative relative five-charge q2."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_standard_charge_q2 as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_standard_charge_q2 import verify


class RelativeStandardChargeQ2Tests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        value = producer.build()
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), value)
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["charge_output_dimension"], 5)
        self.assertEqual(result["h_q2_diagonal"], "-108*(1 + sqrt(3))/5")
        self.assertTrue(result["coefficient_forms_replayed"])
        self.assertTrue(result["cohomology_descent_replayed"])
        self.assertIn(
            "after local gauge reduction",
            json.loads(producer.OUTPUT.read_text())["identities"]["imported_quotient_domains"]["stabilizer"],
        )

    def test_records_not_repairs(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        self.assertTrue(value["classification"]["five_charge_q2_on_standard_radiative_cohomology"])
        self.assertFalse(value["classification"]["direct_f2_repaired"])
        self.assertFalse(value["classification"]["off_shell_local_jet_charge_q2"])
        self.assertFalse(value["classification"]["arity_three_authorized"])

    def test_false_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        for key in (
            "exceptional_and_global_charge_q2_included",
            "off_shell_local_jet_charge_q2",
            "support_local_bv_koszul_extension",
            "direct_f2_repaired",
            "arity_three_authorized",
            "causal_observable_particle_or_quantum_claim",
        ):
            mutant = deepcopy(json.loads(producer.OUTPUT.read_text()))
            mutant["classification"][key] = True
            with self.assertRaises(ValidationError):
                Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
