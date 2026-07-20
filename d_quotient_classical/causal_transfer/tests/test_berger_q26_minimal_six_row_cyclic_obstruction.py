from __future__ import annotations

import copy
import unittest

from d_quotient_classical.causal_transfer import (
    berger_q26_minimal_six_row_cyclic_obstruction as theorem,
)
from d_quotient_classical.causal_transfer import (
    verify_berger_q26_minimal_six_row_cyclic_obstruction as independent,
)


class BergerQ26MinimalSixRowCyclicObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = theorem.build_payload()
        cls.value = theorem.build()

    def test_certificate_validates(self) -> None:
        theorem.validate(self.value)

    def test_complete_six_row_profile_is_unique(self) -> None:
        audit = self.value["rank_audit"]
        self.assertEqual(audit["complete_six_row_profiles"], [[0, 5, 1, 0]])
        self.assertEqual(audit["six_row_extended_ranks"], [12, 45, 41, 12])

    def test_non_degenerate_pairing_is_rank_obstructed(self) -> None:
        self.assertEqual(
            self.value["obstruction"]["simultaneous_system_status"],
            "INCONSISTENT_BEFORE_PBW_COEFFICIENT_SOLVE",
        )
        self.assertEqual(
            self.value["rank_audit"]["minimum_pairing_radical_dimension"], 4
        )
        self.assertFalse(
            self.value["classification"]["six_row_cyclic_BV_extension_exists"]
        )

    def test_next_bound_is_ten_but_not_sufficient(self) -> None:
        bound = self.value["next_lower_bound"]
        self.assertEqual(bound["total_added_rows_at_least"], 10)
        self.assertEqual(
            self.value["rank_audit"]["unique_rank_minimal_cyclic_additions"],
            [0, 5, 5, 0],
        )
        self.assertFalse(self.value["classification"]["ten_row_extension_sufficient"])

    def test_decoupled_control_preserves_old_defects(self) -> None:
        control = self.payload["decoupled_sparse_control"]
        self.assertEqual(control["q_old_old"]["nonzero_sparse_entries"], 1018)
        self.assertEqual(control["A_old_old"]["nonzero_sparse_entries"], 470)
        self.assertEqual(control["q_square_nonzero_sparse_entries"], 157)
        self.assertEqual(control["A_q_commutator_nonzero_sparse_entries"], 207)

    def test_hadamard_promotion_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["classification"]["Hadamard_or_quantum_claim"] = True
        with self.assertRaises(Exception):
            theorem.validate(mutant)

    def test_ten_row_sufficiency_promotion_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["classification"]["ten_row_extension_sufficient"] = True
        with self.assertRaises(Exception):
            theorem.validate(mutant)

    def test_independent_rank_backend_agrees(self) -> None:
        replay = independent._rank_replay()
        self.assertEqual(replay["profiles"], [[0, 5, 1, 0]])
        self.assertEqual(replay["deficits"], {"-1:2": 0, "0:1": 4})
        self.assertEqual(
            replay["cyclic_profiles_through_ten_rows"], [[0, 5, 5, 0]]
        )


if __name__ == "__main__":
    unittest.main()
