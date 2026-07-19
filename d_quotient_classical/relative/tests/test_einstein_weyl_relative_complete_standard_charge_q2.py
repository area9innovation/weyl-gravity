"""Tests for the complete-standard relative five-charge q2."""

from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.relative import einstein_weyl_relative_complete_standard_charge_q2 as producer
from d_quotient_classical.relative.verify_einstein_weyl_relative_complete_standard_charge_q2 import verify


class RelativeCompleteStandardChargeQ2Tests(unittest.TestCase):
    def test_outputs_current(self) -> None:
        value = producer.build()
        self.assertEqual(json.loads(producer.OUTPUT.read_text()), value)
        self.assertEqual(producer.REPORT.read_text(), producer._report())

    def test_independent_replay(self) -> None:
        result = verify()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["standard_blocks"], 4)
        self.assertEqual(result["charge_outputs"], 5)
        self.assertEqual(result["physical_ell1_q2_multiplier"], "6")
        self.assertEqual(result["homogeneous_H_hessian_rank"], 1)
        self.assertEqual(result["twist_H_hessian_rank_per_real_harmonic"], 1)
        self.assertEqual(result["cross_block_terms"], 0)

    def test_scope_is_complete_standard_source_only(self) -> None:
        value = json.loads(producer.OUTPUT.read_text())
        flags = value["classification"]
        self.assertTrue(flags["complete_standard_source_five_charge_q2"])
        self.assertTrue(flags["physical_ell1_all_momenta_included"])
        self.assertTrue(flags["homogeneous_generalized_block_included"])
        self.assertTrue(flags["axial_twist_block_included"])
        self.assertFalse(flags["extra_weyl_target_cofiber_inputs_included"])
        self.assertFalse(flags["off_shell_local_jet_charge_q2"])

    def test_false_promotions_rejected(self) -> None:
        schema = json.loads(producer.SCHEMA.read_text())
        for key in (
            "extra_weyl_target_cofiber_inputs_included",
            "bounded_or_smooth_tangent_cone_solved_by_this_artifact",
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
