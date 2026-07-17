from __future__ import annotations

import unittest

from d_quotient_classical.backreacted_clock import (
    berger_super_cotangent_redefinition_convention as convention,
)


class SuperCotangentConventionTests(unittest.TestCase):
    def test_certified_shear_replays(self) -> None:
        replay = convention.scientific_replay()
        self.assertTrue(replay["all_64_rows_match"])
        self.assertEqual(replay["odd_sign_omission_mutation_defect_rows"], [49, 50, 51, 52])

    def test_odd_sign_mutation_is_nonzero(self) -> None:
        mutant, _ = convention._generated_shear(omit_odd_input_sign=True)
        certified = convention.coupled.maxwell_covariant_ghost_shear()
        self.assertEqual(
            [row for row in range(convention.coupled.TOTAL_ROWS) if mutant[row] != certified[row]],
            [49, 50, 51, 52],
        )

    def test_claim_boundary_fails_closed(self) -> None:
        value = convention.build()
        self.assertFalse(value["claim_flags"]["FULL_BV_ELL3_REDEFINITION_COMPUTED"])
        self.assertFalse(value["claim_flags"]["CYCLIC_DEFORMATION_CLASS_DECIDED"])
        self.assertFalse(value["claim_flags"]["QUANTUM_CLAIM"])


if __name__ == "__main__":
    unittest.main()
