import unittest

from local_bv.curvature import EPSILON, RIEMANN
from local_bv.tensors import TensorExpression, TensorFactor, TensorMonomial, TensorSpec


class AbstractTensorTests(unittest.TestCase):
    def test_riemann_signed_symmetries_and_pair_exchange(self) -> None:
        original = TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
        first_swap = TensorMonomial((TensorFactor(RIEMANN, (1, 0, 2, 3)),))
        second_swap = TensorMonomial((TensorFactor(RIEMANN, (0, 1, 3, 2)),))
        pair_exchange = TensorMonomial((TensorFactor(RIEMANN, (2, 3, 0, 1)),))
        self.assertFalse(TensorExpression({original: 1, first_swap: 1}))
        self.assertFalse(TensorExpression({original: 1, second_swap: 1}))
        self.assertFalse(TensorExpression({original: 1, pair_exchange: -1}))

    def test_dummy_renaming_and_even_factor_order_are_canonical(self) -> None:
        first = TensorMonomial(
            (
                TensorFactor(RIEMANN, (8, 3, 5, 1)),
                TensorFactor(RIEMANN, (8, 3, 5, 1)),
            )
        )
        renamed_and_reordered = TensorMonomial(
            (
                TensorFactor(RIEMANN, (19, 7, 2, 11)),
                TensorFactor(RIEMANN, (19, 7, 2, 11)),
            )
        )
        self.assertEqual(
            TensorExpression.monomial(first),
            TensorExpression.monomial(renamed_and_reordered),
        )

    def test_free_index_permutations_are_not_erased(self) -> None:
        original = TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
        non_symmetry_permutation = TensorMonomial(
            (TensorFactor(RIEMANN, (0, 2, 1, 3)),)
        )
        self.assertNotEqual(
            TensorExpression.monomial(original),
            TensorExpression.monomial(non_symmetry_permutation),
        )

    def test_odd_identical_factor_squares_to_zero(self) -> None:
        ghost = TensorSpec.without_slot_symmetry(
            "test_ghost", 0, grassmann_parity=1
        )
        square = TensorMonomial((TensorFactor(ghost, ()), TensorFactor(ghost, ())))
        self.assertFalse(TensorExpression.monomial(square))

    def test_distinct_odd_factors_anticommute(self) -> None:
        ghost_a = TensorSpec.without_slot_symmetry(
            "test_ghost_a", 0, grassmann_parity=1
        )
        ghost_b = TensorSpec.without_slot_symmetry(
            "test_ghost_b", 0, grassmann_parity=1
        )
        ab = TensorMonomial((TensorFactor(ghost_a, ()), TensorFactor(ghost_b, ())))
        ba = TensorMonomial((TensorFactor(ghost_b, ()), TensorFactor(ghost_a, ())))
        self.assertEqual(TensorExpression.monomial(ab), -TensorExpression.monomial(ba))

    def test_epsilon_is_antisymmetric_and_parity_odd(self) -> None:
        epsilon = TensorMonomial((TensorFactor(EPSILON, (0, 1, 2, 3)),))
        swapped = TensorMonomial((TensorFactor(EPSILON, (1, 0, 2, 3)),))
        expression = TensorExpression.monomial(epsilon)
        self.assertFalse(TensorExpression({epsilon: 1, swapped: 1}))
        self.assertEqual(expression.parity_transform(), -expression)
        self.assertEqual(expression.parity_transform().parity_transform(), expression)


if __name__ == "__main__":
    unittest.main()
