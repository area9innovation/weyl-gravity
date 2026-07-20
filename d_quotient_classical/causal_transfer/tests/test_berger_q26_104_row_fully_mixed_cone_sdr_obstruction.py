from __future__ import annotations

from copy import deepcopy
import unittest

from jsonschema import Draft202012Validator, ValidationError

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_fully_mixed_cone_sdr_obstruction as subject,
)
from d_quotient_classical.causal_transfer import (
    verify_berger_q26_104_row_fully_mixed_cone_sdr_obstruction as verifier,
)


class FullyMixedConeSDRObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = subject.exact_audit()
        cls.certificate = subject.build()
        cls.schema = subject._load(subject.SCHEMA)

    def test_mixed_cone_is_nilpotent_and_equivariant(self) -> None:
        checks = self.audit["checks"]
        self.assertTrue(checks["q_cone_square_zero"])
        self.assertTrue(checks["fully_mixed_evolution_commutes"])

    def test_specialized_cohomology_mismatch(self) -> None:
        self.assertEqual(
            self.audit["cone_homology_dimensions"],
            {"-1": 13, "0": 57, "1": 57, "2": 13},
        )
        self.assertEqual(
            self.audit["retained_homology_dimensions"],
            {"-1": 1, "0": 1, "1": 1, "2": 1},
        )

    def test_fail_closed_claim_boundary(self) -> None:
        flags = self.certificate["classification"]
        self.assertFalse(flags["retained_q26_SDR_exists"])
        self.assertFalse(flags["all_non_cone_104_row_completions_obstructed"])
        mutated = deepcopy(self.certificate)
        mutated["classification"]["retained_q26_SDR_exists"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutated)

    def test_independent_verifier(self) -> None:
        verifier.verify()


if __name__ == "__main__":
    unittest.main()
