from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from transfer.berger_retained_mixed_ell3_physical_cyclicity_certificate import (
    OUTPUT,
    SCHEMA,
    build,
)
from transfer.verify_berger_retained_mixed_ell3_physical_cyclicity import verify


class BergerRetainedMixedEll3PhysicalCyclicityTests(unittest.TestCase):
    def test_exact_physical_cyclicity(self) -> None:
        value = json.loads(OUTPUT.read_text())
        diagnostics = value["exact_replay"]["diagnostics"]
        self.assertEqual(diagnostics["physical_quartic_coefficient_count"], 25_662)
        self.assertEqual(diagnostics["physical_quartic_cyclicity_defect_count"], 0)
        self.assertEqual(
            diagnostics["Maxwell_pairing_weight_mutation_defect_count"], 17_108
        )
        self.assertEqual(
            diagnostics["nonphysical_ghost_antifield_completion_coefficient_count"],
            288,
        )
        self.assertEqual(
            diagnostics["physical_pairing_weight_ledger"],
            {
                "gravity": {
                    "signed_odd_pairing_entries": ["-1"],
                    "absolute_field_equation_weights": ["1"],
                    "row_count": 10,
                },
                "Maxwell": {
                    "signed_odd_pairing_entries": ["2"],
                    "absolute_field_equation_weights": ["2"],
                    "row_count": 4,
                },
            },
        )

    def test_persisted_certificate_reproduces(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build(run_scientific=False))
        self.assertEqual(value, verify())

    def test_full_BV_and_quantum_overclaims_fail_closed(self) -> None:
        value = json.loads(OUTPUT.read_text())
        validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
        for flag in (
            "FULL_RETAINED_BV_ELL3_CYCLICITY_INDEPENDENTLY_REPLAYED",
            "RESIDUAL_BRANCH_PROJECTION_COMPUTED",
            "TOPOLOGICAL_DEFORMATION_DIRECTION_CLASSIFIED",
            "QME_RESTORED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(value)
            mutant["claim_flags"][flag] = True
            self.assertTrue(list(validator.iter_errors(mutant)), flag)


if __name__ == "__main__":
    unittest.main()
