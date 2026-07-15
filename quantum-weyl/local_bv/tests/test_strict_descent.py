import unittest
from fractions import Fraction

from local_bv.strict_descent import (
    strict_candidate_descent_analysis,
    strict_density_descent,
)


class StrictDensityDescentTests(unittest.TestCase):
    def test_coefficients_are_solved_from_exact_rows(self) -> None:
        expected_coefficients = (
            Fraction(1),
            Fraction(-1),
            Fraction(1, 2),
            Fraction(-1, 6),
            Fraction(1, 24),
        )
        expected_ratios = (
            Fraction(1),
            Fraction(1, 2),
            Fraction(1, 3),
            Fraction(1, 4),
        )
        for ghost_lift in (False, True):
            tower = strict_density_descent(ghost_lift)
            self.assertEqual(tower["coefficients"], expected_coefficients)
            self.assertEqual(
                tower["brst_to_horizontal_ratios"], expected_ratios
            )

    def test_towers_have_adjacent_bidegrees_and_closed_bottoms(self) -> None:
        for ghost_lift, start in ((False, 0), (True, 1)):
            tower = strict_density_descent(ghost_lift)
            self.assertEqual(tower["form_degrees"], (4, 3, 2, 1, 0))
            self.assertEqual(
                tower["ghost_numbers"], tuple(range(start, start + 5))
            )
            differential = tower["differential"]
            self.assertFalse(tower["tower"][-1].brst(differential))

    def test_candidate_statuses_remain_scope_separated(self) -> None:
        analysis = strict_candidate_descent_analysis()
        self.assertEqual(len(analysis["computed_candidates"]), 4)
        self.assertEqual(len(analysis["not_computed_candidates"]), 2)
        self.assertEqual(len(analysis["trivialized_candidates"]), 2)
        self.assertIn("ANOM_OMEGA_E4", analysis["not_computed_candidates"])


if __name__ == "__main__":
    unittest.main()
