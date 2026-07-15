from fractions import Fraction
import unittest

from local_bv import Expression, LocalJetAlgebra


class AlgebraTests(unittest.TestCase):
    def setUp(self) -> None:
        self.algebra = LocalJetAlgebra(4)

    def test_odd_jets_anticommute_and_square_to_zero(self) -> None:
        xi0 = self.algebra.var("xi", (0,))
        xi1 = self.algebra.var("xi", (1,))
        self.assertEqual(xi0 * xi1, -(xi1 * xi0))
        self.assertEqual(xi0 * xi0, Expression())

    def test_even_and_odd_jets_commute_without_extra_sign(self) -> None:
        metric = self.algebra.var("g", (0, 1))
        omega = self.algebra.var("omega")
        self.assertEqual(metric * omega, omega * metric)

    def test_total_derivative_is_an_exact_even_derivation(self) -> None:
        left = self.algebra.var("g", (0, 0))
        right = self.algebra.var("omega")
        product_rule = self.algebra.total_derivative(left, 2) * right + left * self.algebra.total_derivative(right, 2)
        self.assertEqual(self.algebra.total_derivative(left * right, 2), product_rule)

    def test_rational_coefficients_and_canonical_hash_are_order_independent(self) -> None:
        g = self.algebra.var("g", (0, 0))
        omega = self.algebra.var("omega")
        first = Fraction(1, 3) * g + Fraction(2, 5) * omega
        second = Fraction(2, 5) * omega + Fraction(1, 3) * g
        self.assertEqual(first, second)
        self.assertEqual(first.canonical_hash(), second.canonical_hash())
        self.assertNotIn(".", str(first.canonical_payload()["terms"][0]["coefficient"]))


if __name__ == "__main__":
    unittest.main()
