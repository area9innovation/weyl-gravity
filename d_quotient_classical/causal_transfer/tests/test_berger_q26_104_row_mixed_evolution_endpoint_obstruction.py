from __future__ import annotations

import unittest

from d_quotient_classical.causal_transfer import (
    berger_q26_104_row_mixed_evolution_endpoint_obstruction as subject,
)


class MixedEvolutionEndpointObstructionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.witness = subject.exact_witness()
        cls.result = subject.build()

    def test_required_rank_is_absent(self) -> None:
        self.assertTrue(self.witness["checks"]["required_rank_23_absent"])
        self.assertEqual(
            self.witness["endpoint_ranks"],
            {"rank_12_correction": 24, "rank_11_correction": 22},
        )

    def test_rational_invariant_line_is_killed(self) -> None:
        self.assertTrue(self.witness["checks"]["frozen_q_kills_invariant_line"])
        self.assertEqual(self.witness["intertwiner_dimension"], 20)

    def test_claim_boundary_is_fail_closed(self) -> None:
        classification = self.result["classification"]
        self.assertFalse(classification["all_rational_104_row_completions_obstructed"])
        self.assertFalse(classification["Hadamard_or_quantum_claim"])

    def test_partial_solver_residue_is_explicit(self) -> None:
        self.assertIn(
            "two-free-differential",
            self.result["partial_solver_disposition"]["remaining_capability"],
        )


if __name__ == "__main__":
    unittest.main()
