from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from spectral.euclidean.generic_background_ghost_n1_n2_hodge_resolvent_reduction import build, validate
from spectral.euclidean.verify_generic_background_ghost_n1_n2_hodge_resolvent_reduction import verify


class GenericGhostN1N2HodgeResolventReductionTests(unittest.TestCase):
    def test_build_and_independent_replay(self) -> None:
        value = build()
        self.assertEqual(value, verify())
        self.assertEqual(value["log_determinant_expansion"]["carrier_count"], 5)

    def test_exact_coefficients(self) -> None:
        value = build()
        n1 = value["log_determinant_expansion"]["n1_carriers"]
        n2 = value["log_determinant_expansion"]["n2_carriers"]
        self.assertEqual([(row["coefficient"]["numerator"], row["coefficient"]["denominator"]) for row in n1], [(1, 1), (-1, 3)])
        self.assertEqual([(row["coefficient"]["numerator"], row["coefficient"]["denominator"]) for row in n2], [(-1, 2), (1, 3), (-1, 18)])
        self.assertEqual(Fraction(1) - Fraction(2, 3), Fraction(1, 3))

    def test_fail_closed_evaluation_flags(self) -> None:
        value = build()
        self.assertFalse(value["claim_flags"]["GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED"])
        self.assertFalse(value["claim_flags"]["GENERIC_GHOST_N2_INSERTION_TRACE_COMPUTED"])
        mutant = deepcopy(value)
        mutant["claim_flags"]["GENERIC_GHOST_N1_INSERTION_TRACE_COMPUTED"] = True
        with self.assertRaises(Exception):
            validate(mutant)

    def test_coefficient_mutation_is_rejected(self) -> None:
        mutant = build()
        mutant["log_determinant_expansion"]["n2_carriers"][1]["coefficient"] = {"numerator": 1, "denominator": 2}
        with self.assertRaises(ValueError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
