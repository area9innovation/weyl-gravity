from __future__ import annotations

from copy import deepcopy
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_noncone_rational_nilpotence_feasibility as subject,
)
from d_quotient_classical.causal_transfer import (
    verify_berger_q26_104_row_noncone_rational_nilpotence_feasibility
    as verifier,
)


class NonconeRationalNilpotenceFeasibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.witness = subject.exact_witness()
        cls.certificate = subject.build()
        cls.schema = subject._load(subject.SCHEMA)

    def test_exact_nilpotence_and_old_blocks(self) -> None:
        self.assertTrue(all(self.witness["checks"].values()))
        self.assertEqual(self.witness["differential_ranks"], [23, 56, 23])

    def test_retained_cohomology_rank_target(self) -> None:
        self.assertEqual(
            self.witness["cohomology_dimensions"], [1, 1, 1, 1]
        )

    def test_fail_closed_scope(self) -> None:
        flags = self.certificate["classification"]
        self.assertFalse(flags["rational_PBW_operator_completion_constructed"])
        self.assertFalse(flags["A104_evolution_lift_constructed"])
        mutated = deepcopy(self.certificate)
        mutated["classification"][
            "rational_PBW_operator_completion_constructed"
        ] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)

    def test_independent_verifier(self) -> None:
        verifier.verify()


if __name__ == "__main__":
    unittest.main()
