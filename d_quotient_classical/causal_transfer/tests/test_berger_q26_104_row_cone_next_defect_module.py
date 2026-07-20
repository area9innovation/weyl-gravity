from __future__ import annotations

import unittest

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_cone_next_defect_module as theorem,
)
from d_quotient_classical.causal_transfer import (
    verify_berger_q26_104_row_cone_next_defect_module as independent,
)


class ConeNextDefectModuleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = theorem.closure_audit()
        cls.value = theorem.build()

    def test_raw_next_defect_ranks(self) -> None:
        self.assertEqual(
            self.payload["raw_ranks"],
            {
                "q": 351,
                "kernel_q": 585,
                "right_lift_cokernel_image": 27,
                "left_adjoint_cokernel_image": 70,
                "combined_next_defect": 97,
            },
        )

    def test_next_defect_closure_is_full(self) -> None:
        self.assertEqual(
            [
                item["certified_independent_columns"]
                for item in self.payload["closure_levels"]
            ],
            [97, 344, 856, 936],
        )
        self.assertEqual(
            self.payload["closure_levels"][-1][
                "minor_determinant_mod_prime"
            ],
            411,
        )

    def test_cone_tower_bound_is_scoped(self) -> None:
        module = self.value["next_defect_module"]
        self.assertEqual(
            module["canonical_tower_total_added_rows_at_least"], 208
        )
        self.assertEqual(
            module["canonical_tower_total_carrier_rows_at_least"], 312
        )
        flags = self.value["classification"]
        self.assertFalse(flags["all_non_cone_104_row_completions_obstructed"])
        self.assertFalse(flags["global_minimum_added_rows_raised_above_104"])
        self.assertFalse(flags["Hadamard_or_quantum_claim"])

    def test_independent_quotient_replay(self) -> None:
        result = independent.replay()
        self.assertEqual(result["levels"], [97, 344, 856, 936])
        self.assertEqual(result["determinant"], 472)


if __name__ == "__main__":
    unittest.main()
