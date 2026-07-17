from __future__ import annotations

from copy import deepcopy
import unittest

from jsonschema import ValidationError

from d_quotient_classical.backreacted_clock.berger_retained_mixed_ell3_constant_field_redefinition import (
    build,
    validate,
)
from d_quotient_classical.backreacted_clock.verify_berger_retained_mixed_ell3_constant_field_redefinition import (
    verify,
)


class RetainedMixedEll3ConstantFieldRedefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_exact_constant_field_trivialization(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify(deepcopy(self.value)))
        verdict = self.value["exact_verdict"]
        self.assertEqual(verdict["coboundary_matrix_shape"], [550, 2690])
        self.assertEqual(verdict["coboundary_rank"], 550)
        self.assertEqual(verdict["cokernel_dimension"], 0)
        self.assertTrue(verdict["target_in_image"])

    def test_exported_primitive_is_compact_and_ternary(self) -> None:
        verdict = self.value["exact_verdict"]
        self.assertEqual(verdict["primitive_nonzero_count"], 51)
        self.assertEqual(verdict["primitive_arity_counts"], {"F2": 0, "F3": 51})
        self.assertTrue(all(row["arity"] == "F3" for row in verdict["primitive"]))

    def test_scoped_g0_claim_boundary(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["CONSTANT_FIELD_PHYSICAL_QUARTIC_TRIVIALIZATION_COMPUTED"])
        self.assertFalse(flags["CYCLIC_DEFORMATION_CLASS_DECIDED"])
        self.assertFalse(flags["FULL_JET_BOUNDED_REDEFINITION_COMPUTED"])
        self.assertFalse(flags["ELL3_NONREMOVABLE"])
        self.assertFalse(flags["ELL3_BRANCH_MIXING_AUTHORIZED"])
        self.assertFalse(flags["QUANTUM_CLAIM"])

    def test_overclaim_mutations_fail(self) -> None:
        for flag in (
            "CYCLIC_DEFORMATION_CLASS_DECIDED",
            "FULL_JET_BOUNDED_REDEFINITION_COMPUTED",
            "ELL3_NONREMOVABLE",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
            "QUANTUM_CLAIM",
        ):
            mutant = deepcopy(self.value)
            mutant["claim_flags"][flag] = True
            with self.assertRaises((ValidationError, ValueError)):
                validate(mutant)

    def test_primitive_coefficient_mutation_fails_independent_replay(self) -> None:
        mutant = deepcopy(self.value)
        mutant["exact_verdict"]["primitive"][0]["coefficient"] = "0"
        with self.assertRaisesRegex(ValueError, "primitive reconstruction"):
            verify(mutant)


if __name__ == "__main__":
    unittest.main()
