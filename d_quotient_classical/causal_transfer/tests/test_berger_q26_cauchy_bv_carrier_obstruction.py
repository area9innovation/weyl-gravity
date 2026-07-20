from __future__ import annotations

import copy
import unittest

from d_quotient_classical.causal_transfer import (
    berger_q26_cauchy_bv_carrier_obstruction as theorem,
)


class BergerQ26CauchyBVCarrierObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = theorem.build()
        cls.payload = theorem.build_payload()

    def test_certificate_validates(self) -> None:
        theorem.validate(self.value)

    def test_declared_class_is_complete_by_formal_evaluation(self) -> None:
        declared = self.value["complete_declared_lift_class"]
        self.assertIn("fixes q_C pointwise", declared["completeness_argument"])
        self.assertEqual(
            declared["unique_member"],
            "imported rejected_candidate_q_Cauchy_104",
        )

    def test_rejected_controls_are_reproduced(self) -> None:
        replay = self.value["exact_replay"]
        self.assertEqual(replay["q_Cauchy_square_nonzero_sparse_entries"], 157)
        self.assertEqual(
            replay["A104_q_Cauchy_commutator_nonzero_sparse_entries"], 207
        )
        self.assertFalse(replay["q_Cauchy_squared_zero"])
        self.assertFalse(replay["A104_commutes_with_q_Cauchy"])

    def test_representation_is_multiplicative(self) -> None:
        representation = theorem._representation()
        d1, d2, d3 = representation[1:]
        self.assertEqual(d1 * d2 - d2 * d1, d3)
        self.assertEqual(d2 * d3 - d3 * d2, 3 * d1)
        self.assertEqual(d3 * d1 - d1 * d3, 3 * d2)

    def test_degreewise_extension_lower_bound(self) -> None:
        bound = self.value["extension_lower_bound"]
        self.assertEqual(bound["degree_0_added_rows_at_least"], 5)
        self.assertEqual(bound["degree_plus1_added_rows_at_least"], 1)
        self.assertEqual(bound["total_added_rows_at_least"], 6)
        self.assertEqual(bound["status"], "NECESSARY_NOT_SUFFICIENT")

    def test_exact_block_ranks(self) -> None:
        self.assertEqual(
            self.payload["square_blocks"]["degree_minus1_to_plus1"]["rank"],
            13,
        )
        self.assertEqual(
            self.payload["square_blocks"]["degree_0_to_plus2"]["rank"], 3
        )
        self.assertEqual(
            [
                self.payload["commutator_blocks"][name]["rank"]
                for name in (
                    "degree_minus1_to_0",
                    "degree_0_to_plus1",
                    "degree_plus1_to_plus2",
                )
            ],
            [13, 15, 5],
        )

    def test_six_rows_are_not_promoted_to_sufficient(self) -> None:
        self.assertFalse(
            self.value["claim_flags"]["BERGER_6_ROW_EXTENSION_SUFFICIENT"]
        )
        self.assertFalse(
            self.value["claim_flags"]["BERGER_ALTERNATIVE_COMPANION_NO_GO"]
        )

    def test_hadamard_mutation_is_rejected(self) -> None:
        mutant = copy.deepcopy(self.value)
        mutant["claim_flags"]["BERGER_HADAMARD_DATA"] = True
        with self.assertRaises(Exception):
            theorem.validate(mutant)


if __name__ == "__main__":
    unittest.main()
