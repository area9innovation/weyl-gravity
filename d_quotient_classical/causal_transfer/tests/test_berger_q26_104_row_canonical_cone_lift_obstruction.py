from __future__ import annotations

import unittest

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_canonical_cone_lift_obstruction as theorem,
)
from d_quotient_classical.causal_transfer import (
    verify_berger_q26_104_row_canonical_cone_lift_obstruction as independent,
)


class CanonicalConeLiftObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = theorem.exact_audit()
        cls.value = theorem.build()

    def test_rational_trivial_representation_is_multiplicative(self) -> None:
        representation = self.audit["representation"]
        self.assertEqual(representation["coefficient_field"], "QQ")
        self.assertTrue(representation["multiplicative"])
        self.assertEqual(
            set(representation["derivative_generators"].values()), {0}
        )

    def test_right_lift_has_normalized_cokernel_witness(self) -> None:
        right = self.audit["right_lift_Dq_equals_qA"]
        self.assertEqual(right["status"], "INCONSISTENT")
        self.assertEqual(right["cokernel_rank"], 1)
        self.assertEqual(right["q_z"], [])
        self.assertEqual(
            right["q_A_z"],
            [[92, "-1022"], [95, "-1022"], [97, "-1022"]],
        )

    def test_free_adjoint_orientation_fails_independently(self) -> None:
        left = self.audit["left_adjoint_lift_Aq_equals_qD"]
        self.assertEqual(left["status"], "INCONSISTENT")
        self.assertEqual(left["cokernel_rank"], 1)
        self.assertEqual(left["ell_transpose_q"], [])
        self.assertTrue(left["ell_transpose_A_q"])

    def test_cone_is_not_overpromoted_to_complete_104_row_no_go(self) -> None:
        classification = self.value["classification"]
        self.assertTrue(classification["canonical_doubled_cone_q_nilpotent"])
        self.assertFalse(
            classification[
                "canonical_doubled_cone_evolution_lift_exists"
            ]
        )
        self.assertFalse(
            classification["all_104_row_completions_obstructed"]
        )
        self.assertFalse(classification["Hadamard_or_quantum_claim"])

    def test_decoupled_mutation_reproduces_frozen_defects(self) -> None:
        control = self.value["decoupled_mutation"]
        self.assertEqual(control["q_square_defects"], 157)
        self.assertEqual(control["A_q_commutator_defects"], 207)
        self.assertEqual(
            control["status"], "REPRODUCES_FROZEN_REJECTED_CONTROL"
        )

    def test_independent_replay(self) -> None:
        self.assertEqual(
            independent.verify(),
            {
                "rank_q": 34,
                "rank_row_stack_q_qA": 35,
                "rank_column_stack_q_Aq": 35,
            },
        )


if __name__ == "__main__":
    unittest.main()
