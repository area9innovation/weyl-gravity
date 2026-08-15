"""Tests for the BT additive flow-rate obstruction."""

from __future__ import annotations

import unittest
from fractions import Fraction

from reverse_physics import bt_euclidean_additive_flow_rate_obstruction as gate


def decode(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class AdditiveFlowRateObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = gate.build()

    def test_all_checks_pass(self) -> None:
        self.assertTrue(self.result["checks"]["ok"])
        self.assertEqual(self.result["checks"]["passed"], 18)

    def test_geometric_mean_gauge_is_exact(self) -> None:
        for row in self.result["exact_rows"]:
            self.assertEqual(sum(row["exponents"]), 0)
            self.assertEqual(decode(row["geometric_mean_gauge_product"]), 1)

    def test_both_additive_rates_decrease(self) -> None:
        unnormalized = [
            decode(row["unnormalized_relative_action_decay"])
            for row in self.result["exact_rows"]
        ]
        normalized = [
            decode(row["normalized_relative_action_decay"])
            for row in self.result["exact_rows"]
        ]
        self.assertTrue(all(b < a for a, b in zip(unnormalized, unnormalized[1:])))
        self.assertTrue(all(b < a for a, b in zip(normalized, normalized[1:])))

    def test_gradient_quotient_moves_in_opposite_direction(self) -> None:
        values = [decode(row["euclidean_gradient_quotient"]) for row in self.result["exact_rows"]]
        self.assertTrue(all(b > a for a, b in zip(values, values[1:])))

    def test_leading_terms_fix_all_three_limits(self) -> None:
        terms = self.result["leading_laurent_terms"]
        self.assertEqual((terms["residual_square"]["exponent"], decode(terms["residual_square"]["coefficient"])), (12, 2))
        self.assertEqual((terms["additive_dissipation"]["exponent"], decode(terms["additive_dissipation"]["coefficient"])), (11, 4))
        self.assertEqual((terms["reciprocal_sum"]["exponent"], decode(terms["reciprocal_sum"]["coefficient"])), (3, 3))
        self.assertEqual((terms["gradient_square"]["exponent"], decode(terms["gradient_square"]["coefficient"])), (24, 6))

    def test_mutating_peak_exponent_breaks_gauge(self) -> None:
        exponents = list(self.result["exact_rows"][0]["exponents"])
        exponents[0] += 1
        self.assertNotEqual(sum(exponents), 0)

    def test_scope_does_not_promote_actual_gradient_failure(self) -> None:
        disposition = self.result["method_disposition"]
        self.assertEqual(disposition["actual_euclidean_gradient_flow_rate"], "NOT_DECIDED")
        self.assertEqual(disposition["interacting_uniform_h_minus_one"], "OPEN")


if __name__ == "__main__":
    unittest.main()
