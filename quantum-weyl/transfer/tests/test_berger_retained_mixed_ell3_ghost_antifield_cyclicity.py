from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator

from transfer.berger_retained_mixed_ell3_ghost_antifield_cyclicity_certificate import (
    OUTPUT,
    SCHEMA,
    build,
)
from transfer.berger_retained_mixed_ell3_ghost_antifield_cyclicity import (
    _transpose_sign,
)
from transfer.verify_berger_retained_mixed_ell3_ghost_antifield_cyclicity import verify


class BergerRetainedMixedEll3GhostAntifieldCyclicityTests(unittest.TestCase):
    def test_suspended_Darboux_sign_table(self) -> None:
        self.assertEqual(_transpose_sign(-1, -1), -1)
        self.assertEqual(_transpose_sign(-1, 0), 1)
        self.assertEqual(_transpose_sign(-1, 2), -1)
        self.assertEqual(_transpose_sign(0, 0), 1)
        self.assertEqual(_transpose_sign(0, 2), -1)
        self.assertEqual(_transpose_sign(2, 2), 1)

    def test_exact_full_BV_cyclicity(self) -> None:
        value = json.loads(OUTPUT.read_text())
        diagnostics = value["exact_replay"]["diagnostics"]
        self.assertEqual(diagnostics["retained_ell3_coefficient_count"], 25_950)
        self.assertEqual(
            diagnostics["ghost_antifield_completion_coefficient_count"], 288
        )
        self.assertEqual(
            diagnostics["ghost_antifield_completion_output_rows"],
            [23, 24, 25, 26, 32, 33, 34],
        )
        self.assertEqual(diagnostics["full_BV_cyclicity_defect_count"], 0)
        self.assertEqual(
            diagnostics["omitted_degree_two_polarization_mutation_defect_count"],
            132,
        )

    def test_persisted_certificate_reproduces(self) -> None:
        value = json.loads(OUTPUT.read_text())
        self.assertEqual(value, build(run_scientific=False))
        self.assertEqual(value, verify())

    def test_quantum_overclaims_fail_closed(self) -> None:
        value = json.loads(OUTPUT.read_text())
        validator = Draft202012Validator(json.loads(SCHEMA.read_text()))
        for flag in (
            "RESIDUAL_BRANCH_PROJECTION_COMPUTED",
            "QME_RESTORED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(value)
            mutant["claim_flags"][flag] = True
            self.assertTrue(list(validator.iter_errors(mutant)), flag)


if __name__ == "__main__":
    unittest.main()
