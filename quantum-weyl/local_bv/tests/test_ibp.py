import unittest

from local_bv.quotient import RelationQuotient
from local_bv.tensors import (
    TensorFactor,
    TensorMonomial,
    TensorSpec,
    total_covariant_derivative,
)


class IntegrationByPartsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = TensorSpec.without_slot_symmetry("A", 0)
        self.b = TensorSpec.without_slot_symmetry("B", 0)

    def divergence(self):
        vector = TensorMonomial(
            (
                TensorFactor(self.a, ()),
                TensorFactor(self.b, (), derivatives=(9,)),
            )
        )
        return total_covariant_derivative(vector, 9)

    def test_total_derivative_uses_exact_covariant_leibniz_rule(self) -> None:
        divergence = self.divergence()
        self.assertEqual(len(divergence.terms), 2)
        self.assertTrue(
            all(monomial.is_complete_contraction() for monomial in divergence.terms)
        )
        self.assertTrue(all(coefficient == 1 for coefficient in divergence.terms.values()))

    def test_ibp_is_a_quotient_by_the_total_divergence(self) -> None:
        divergence = self.divergence()
        quotient = RelationQuotient(divergence.terms, (divergence,))
        self.assertEqual(quotient.relation_rank, 1)
        self.assertEqual(quotient.quotient_dimension, 1)
        self.assertEqual(quotient.free_coordinates(divergence), (0,))

    def test_divergence_index_must_be_uniquely_free(self) -> None:
        scalar = TensorMonomial((TensorFactor(self.a, ()),))
        with self.assertRaisesRegex(ValueError, "unique free index"):
            total_covariant_derivative(scalar, 4)


if __name__ == "__main__":
    unittest.main()
