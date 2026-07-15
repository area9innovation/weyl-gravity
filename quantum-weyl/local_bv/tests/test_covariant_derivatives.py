import unittest

from local_bv.covariant_derivatives import (
    COMMUTATOR_CONVENTION,
    covariant_commutator_relation,
)
from local_bv.quotient import RelationQuotient
from local_bv.tensors import TensorFactor, TensorSpec


class CovariantDerivativeTests(unittest.TestCase):
    def factor(self, rank: int) -> TensorFactor:
        spec = TensorSpec.without_slot_symmetry(f"T{rank}", rank)
        return TensorFactor(spec, tuple(range(rank)))

    def test_declared_commutator_convention_is_stable(self) -> None:
        self.assertEqual(
            COMMUTATOR_CONVENTION,
            "[nabla_a,nabla_b] T_{c1...cr} = "
            "-sum_i R^d{}_{ci ab} T_{c1...d...cr}",
        )

    def test_scalar_covariant_derivatives_commute(self) -> None:
        relation = covariant_commutator_relation(self.factor(0), 1, 2)
        self.assertEqual(len(relation.terms), 2)
        quotient = RelationQuotient(relation.terms, (relation,))
        self.assertEqual(quotient.relation_rank, 1)
        self.assertFalse(any(quotient.free_coordinates(relation)))

    def test_covector_and_rank_two_curvature_actions(self) -> None:
        for rank, expected_terms in ((1, 3), (2, 4)):
            factor = self.factor(rank)
            left, right = rank + 1, rank + 2
            relation = covariant_commutator_relation(factor, left, right)
            reversed_relation = covariant_commutator_relation(factor, right, left)
            with self.subTest(rank=rank):
                self.assertEqual(len(relation.terms), expected_terms)
                self.assertEqual(relation, -reversed_relation)
                self.assertEqual(
                    sum(
                        1
                        for monomial in relation.terms
                        if any(item.spec.name == "Riemann" for item in monomial.factors)
                    ),
                    rank,
                )

    def test_preexisting_derivatives_fail_closed(self) -> None:
        factor = TensorFactor(
            TensorSpec.without_slot_symmetry("T", 1),
            (0,),
            derivatives=(1,),
        )
        with self.assertRaisesRegex(ValueError, "no existing derivatives"):
            covariant_commutator_relation(factor, 2, 3)


if __name__ == "__main__":
    unittest.main()
