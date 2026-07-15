import unittest

from local_bv.curvature import (
    RIEMANN,
    differential_bianchi_relation,
    pair_partitions,
    two_derivative_contraction_from_pairing,
    two_derivative_curvature_analysis,
)
from local_bv.tensors import TensorFactor, TensorMonomial


class TwoDerivativeCurvatureTests(unittest.TestCase):
    def test_all_ten_slot_pairings_are_generated(self) -> None:
        pairings = tuple(pair_partitions(tuple(range(10))))
        self.assertEqual(len(pairings), 945)
        self.assertTrue(
            all(
                two_derivative_contraction_from_pairing(pairing).is_complete_contraction()
                for pairing in pairings
            )
        )

    def test_outer_derivative_preserves_differential_bianchi(self) -> None:
        monomial = TensorMonomial(
            (
                TensorFactor(
                    RIEMANN,
                    (2, 3, 4, 5),
                    derivatives=(0, 1),
                ),
            )
        )
        relation = differential_bianchi_relation(monomial, 0)
        self.assertEqual(len(relation.terms), 3)
        self.assertTrue(
            all(factor.derivatives[0] == 0 for term in relation.terms for factor in term.factors)
        )

    def test_bridge_bianchi_quotient_has_exact_generated_dimensions(self) -> None:
        analysis = two_derivative_curvature_analysis()
        self.assertEqual(analysis["raw_pairing_count"], 945)
        self.assertEqual(analysis["symmetry_canonical_monomial_count"], 14)
        self.assertEqual(analysis["algebraic_bianchi_relation_count"], 6)
        self.assertEqual(analysis["algebraic_bianchi_rank"], 3)
        self.assertEqual(analysis["differential_bianchi_relation_count"], 16)
        self.assertEqual(analysis["differential_bianchi_rank"], 8)
        self.assertEqual(analysis["combined_relation_rank"], 8)
        self.assertEqual(analysis["quotient_dimension"], 6)


if __name__ == "__main__":
    unittest.main()
