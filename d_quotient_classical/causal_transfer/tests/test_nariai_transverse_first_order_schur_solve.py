import unittest

from d_quotient_classical.causal_transfer.nariai_transverse_first_order_schur_solve import (
    solve,
)


class TransverseFirstOrderSchurSolveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = solve()

    def test_complete_map_is_injective(self):
        self.assertEqual(self.data["linear_system"]["coefficient_map_shape"], [60, 45])
        self.assertEqual(self.data["linear_system"]["coefficient_map_rank"], 45)

    def test_all_rows_have_unique_solutions(self):
        self.assertEqual(self.data["linear_system"]["augmented_ranks"], [45] * 9)
        self.assertEqual(self.data["linear_system"]["free_parameter_counts"], [0] * 9)

    def test_gauge_closure_and_claim_boundary(self):
        self.assertEqual(self.data["corrected_gauge_residual"]["nonzero_coefficients"], 0)
        self.assertFalse(self.data["interpretation"]["action_derived_identification"])
        self.assertFalse(self.data["interpretation"]["cyclicity_with_authoritative_action_pairing"])


if __name__ == "__main__":
    unittest.main()
