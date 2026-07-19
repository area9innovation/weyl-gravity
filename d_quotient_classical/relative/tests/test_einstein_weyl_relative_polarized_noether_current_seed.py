"""Certificate tests for the polarized relative-current seed."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_polarized_noether_current_seed as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_polarized_noether_current_seed import verify


class RelativePolarizedNoetherCurrentSeedTests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        value = producer.build()
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), value)
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["spatial_fixture"], "3*x/8")
        self.assertFalse(result["divergence_cone"])

    def test_downstream_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        value = json.loads(producer.OUTPUT.read_text())
        for key in (
            "off_shell_divergence_cone_certified",
            "slice_integral_matches_complete_five_charge_q2",
            "cyclic_dual_rows_certified",
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
