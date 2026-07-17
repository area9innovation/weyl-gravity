from __future__ import annotations

from copy import deepcopy
import unittest

from d_quotient_classical.backreacted_clock.berger_retained_46_stf2_physical_helicity_filtered_quotient import (
    build,
    validate,
)
from d_quotient_classical.backreacted_clock.verify_berger_retained_46_stf2_physical_helicity_filtered_quotient import (
    verify,
)


class Retained46STF2PhysicalHelicityFilteredQuotientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_exact_projective_physical_module(self) -> None:
        validate(self.value)
        self.assertEqual(self.value, verify())
        cohomology = self.value["full_Berger_null_symbol_cohomology"]
        self.assertEqual(cohomology["cohomology_dimensions"], [0, 6, 6, 0])
        self.assertEqual(cohomology["physical_degree_zero_rank"], 2)
        self.assertEqual(
            self.value["filtered_principal_module"]["generalized_wave_rank_over_Q_sqrt10"],
            4,
        )

    def test_pairing_and_helicity_are_normalized(self) -> None:
        fibre = self.value["normalized_standard_null_fibre"]
        self.assertEqual(fibre["induced_cyclic_pairing"], [["1", "0"], ["0", "1"]])
        self.assertEqual(fibre["complex_helicity_weights"], ["+2i", "-2i"])
        self.assertTrue(fibre["linearized_Weyl_isomorphism"])

    def test_raw_V2_shortcuts_remain_forbidden(self) -> None:
        contract = self.value["V2_receiving_contract"]
        self.assertFalse(contract["raw_10x10_diagonalization_authorized"])
        self.assertFalse(contract["raw_Pi_TT_V2_Pi_TT_compression_is_an_invariant_verdict"])
        self.assertFalse(contract["V2_filtered_descent_computed_here"])

    def test_overclaim_mutations_fail(self) -> None:
        for flag in (
            "GLOBAL_TWO_COLUMN_HELICITY_FRAME_CERTIFIED",
            "V2_FILTERED_DESCENT_COMPUTED",
            "SUBPRINCIPAL_BRANCH_ANCHOR_AVAILABLE",
            "ELL3_BRANCH_MIXING_AUTHORIZED",
        ):
            mutant = deepcopy(self.value)
            mutant["claim_flags"][flag] = True
            with self.assertRaisesRegex(ValueError, "claim boundary"):
                validate(mutant)

    def test_projector_mutation_fails(self) -> None:
        mutant = deepcopy(self.value)
        mutant["exact_checks"]["TT_projector_idempotent_mod_null_relation"] = False
        with self.assertRaisesRegex(ValueError, "exact check"):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
