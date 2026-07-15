import unittest

from local_bv.curvature import (
    RIEMANN,
    differential_bianchi_relation,
    one_derivative_contraction_from_pairing,
    one_derivative_curvature_analysis,
    pair_partitions,
)
from local_bv.tensors import TensorFactor, TensorMonomial


class DifferentialCurvatureTests(unittest.TestCase):
    def test_all_ten_slot_pairings_are_generated(self) -> None:
        pairings = tuple(pair_partitions(tuple(range(10))))
        self.assertEqual(len(pairings), 945)
        self.assertEqual(len(set(pairings)), 945)
        for pairing in pairings:
            self.assertTrue(
                one_derivative_contraction_from_pairing(
                    pairing
                ).is_complete_contraction()
            )

    def test_differential_bianchi_is_a_generated_relation(self) -> None:
        monomial = TensorMonomial(
            (TensorFactor(RIEMANN, (1, 2, 3, 4), derivatives=(0,)),)
        )
        relation = differential_bianchi_relation(monomial, 0)
        self.assertTrue(relation)
        self.assertEqual(len(relation.terms), 3)

    def test_exact_one_derivative_quotient(self) -> None:
        analysis = one_derivative_curvature_analysis()
        self.assertEqual(analysis["raw_pairing_count"], 945)
        self.assertEqual(analysis["symmetry_canonical_monomial_count"], 12)
        self.assertEqual(analysis["algebraic_bianchi_relation_count"], 6)
        self.assertEqual(analysis["algebraic_bianchi_rank"], 3)
        self.assertEqual(analysis["differential_bianchi_relation_count"], 16)
        self.assertEqual(analysis["differential_bianchi_rank"], 8)
        self.assertEqual(analysis["combined_relation_rank"], 8)
        self.assertEqual(analysis["quotient_dimension"], 4)
        self.assertEqual(analysis["quotient"].free_columns, (5, 6, 7, 11))

    def test_wrong_derivative_order_fails_closed(self) -> None:
        no_derivative = TensorMonomial(
            (TensorFactor(RIEMANN, (0, 1, 2, 3)),)
        )
        with self.assertRaisesRegex(ValueError, "a derivative"):
            differential_bianchi_relation(no_derivative, 0)


if __name__ == "__main__":
    unittest.main()
