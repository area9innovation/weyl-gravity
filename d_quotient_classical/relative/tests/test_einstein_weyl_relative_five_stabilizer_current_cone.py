"""Fast certificate checks for the five-stabilizer current cone."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_five_stabilizer_current_cone as producer


class RelativeFiveStabilizerCurrentConeTests(unittest.TestCase):
    def test_stored_certificate_is_strict_and_complete(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        producer.validate(value)
        self.assertEqual(list(value["records"]), ["H", "J_1", "J_2", "J_3", "P_x"])
        self.assertTrue(all(record["divergence_defect_count"] == 0 for record in value["records"].values()))

    def test_downstream_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        value = json.loads(producer.OUTPUT.read_text())
        for key in (
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
