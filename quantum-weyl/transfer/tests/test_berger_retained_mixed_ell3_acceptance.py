from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from transfer.berger_retained_mixed_ell3_acceptance_certificate import OUTPUT, SCHEMA, build
from transfer.verify_berger_retained_mixed_ell3_acceptance import verify


class BergerRetainedMixedEll3AcceptanceTests(unittest.TestCase):
    def test_persisted_exact_acceptance(self) -> None:
        value = json.loads(OUTPUT.read_text())
        diagnostics = value["exact_replay"]["diagnostics"]
        self.assertEqual(diagnostics["retained_ell3_coefficient_count"], 25_950)
        self.assertEqual(diagnostics["contact_missing_count"], 0)
        self.assertEqual(diagnostics["contact_extra_count"], 0)
        self.assertEqual(diagnostics["contact_changed_count"], 0)
        self.assertEqual(diagnostics["exchange_outer_inner_pair_counts"], {
            "gravity_outer_mixed_inner": 144,
            "mixed_outer_gravity_inner": 0,
            "mixed_outer_mixed_inner": 0,
        })
        self.assertEqual(diagnostics["exchange_unshuffle_contribution_counts"], {
            "gravity_outer_mixed_inner": 324,
            "mixed_outer_gravity_inner": 0,
            "mixed_outer_mixed_inner": 0,
        })
        self.assertEqual(diagnostics["exchange_full_coefficient_counts"], {
            "gravity_outer_mixed_inner": 342,
            "mixed_outer_gravity_inner": 0,
            "mixed_outer_mixed_inner": 0,
        })
        self.assertEqual(diagnostics["exchange_full_nonzero_output_rows"], {
            "gravity_outer_mixed_inner": [38],
            "mixed_outer_gravity_inner": [],
            "mixed_outer_mixed_inner": [],
        })
        self.assertEqual(diagnostics["exchange_projection_contribution_counts"], {
            "gravity_outer_mixed_inner": 0,
            "mixed_outer_gravity_inner": 0,
            "mixed_outer_mixed_inner": 0,
        })
        self.assertEqual(diagnostics["exchange_final_coefficient_counts"], {
            "gravity_outer_mixed_inner": 0,
            "mixed_outer_gravity_inner": 0,
            "mixed_outer_mixed_inner": 0,
        })
        self.assertEqual(
            diagnostics["exchange_projection_mutation"]["final_coefficient_counts"],
            {
                "gravity_outer_mixed_inner": 342,
                "mixed_outer_gravity_inner": 0,
                "mixed_outer_mixed_inner": 0,
            },
        )
        self.assertTrue(
            diagnostics["exchange_projection_mutation"]["mutant_rejected"]
        )
        self.assertTrue(diagnostics["producer_exchange_ledger_independently_matched"])
        self.assertEqual(diagnostics["retained_arity_three_defect_count"], 0)
        self.assertGreater(diagnostics["mutation_defect_count"], 0)

    def test_persisted_certificate_and_fast_verifier(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build(run_scientific=False))
        self.assertEqual(value, verify())

    def test_fail_closed_claim_mutations(self) -> None:
        value = json.loads(OUTPUT.read_text())
        validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
        for flag in (
            "RETAINED_MIXED_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED",
            "EINSTEIN_EXTRA_WEYL_BRANCH_MIXING_COMPUTED",
            "TOPOLOGICAL_DIRECTION_CLASSIFIED",
            "NEGATIVE_PHYSICAL_DIRECTION_INTRODUCED",
            "REPOSITORY_BV_QME_RESTORED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(value)
            mutant["claim_flags"][flag] = True
            self.assertTrue(list(validator.iter_errors(mutant)), flag)
        mutant = deepcopy(value)
        mutant["exact_replay"]["diagnostics"]["exchange_final_coefficient_counts"]["gravity_outer_mixed_inner"] = 1
        self.assertTrue(list(validator.iter_errors(mutant)))


if __name__ == "__main__":
    unittest.main()
