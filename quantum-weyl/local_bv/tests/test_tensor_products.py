import unittest

from local_bv.tensors import (
    TensorExpression,
    TensorFactor,
    TensorMonomial,
    TensorSpec,
)


class TensorProductTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vector = TensorSpec.without_slot_symmetry("V", 1)
        self.covector = TensorSpec.without_slot_symmetry("W", 1)

    def monomial(self, spec: TensorSpec, index: int) -> TensorMonomial:
        return TensorMonomial((TensorFactor(spec, (index,)),))

    def test_default_product_alpha_renames_colliding_indices(self) -> None:
        left = self.monomial(self.vector, 0)
        right = self.monomial(self.covector, 0)
        product = left.tensor_product(right)
        self.assertEqual(product.index_multiplicities(), {0: 1, 1: 1})
        self.assertFalse(product.is_complete_contraction())

    def test_explicit_index_map_creates_declared_contraction(self) -> None:
        left = self.monomial(self.vector, 7)
        right = self.monomial(self.covector, 3)
        product = left.tensor_product(right, index_map={3: 7})
        self.assertEqual(product.index_multiplicities(), {7: 2})
        self.assertTrue(product.is_complete_contraction())

    def test_expression_product_is_bilinear(self) -> None:
        left = TensorExpression.monomial(self.monomial(self.vector, 0))
        right = TensorExpression.monomial(self.monomial(self.covector, 1))
        # TensorExpression canonicalization independently normalizes each free
        # index to zero before the product is formed.
        product = (2 * left).tensor_product(3 * right, index_map={0: 0})
        self.assertEqual(tuple(product.terms.values()), (6,))
        self.assertTrue(next(iter(product.terms)).is_complete_contraction())

    def test_unknown_or_overused_index_map_fails_closed(self) -> None:
        left = TensorMonomial(
            (
                TensorFactor(self.vector, (0,)),
                TensorFactor(self.covector, (0,)),
            )
        )
        right = self.monomial(self.vector, 1)
        with self.assertRaisesRegex(ValueError, "unknown right indices"):
            left.tensor_product(right, index_map={9: 0})
        with self.assertRaisesRegex(ValueError, "occur over twice"):
            left.tensor_product(right, index_map={1: 0})


if __name__ == "__main__":
    unittest.main()
