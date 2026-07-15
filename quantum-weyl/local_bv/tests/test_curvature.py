import unittest

from local_bv.curvature import (
    RIEMANN,
    bianchi_relation,
    contraction_from_pairing,
    pair_partitions,
    quadratic_curvature_analysis,
)
from local_bv.tensors import TensorFactor, TensorMonomial


class QuadraticCurvatureTests(unittest.TestCase):
    def test_pairing_generator_is_complete_and_exhaustive(self) -> None:
        pairings = tuple(pair_partitions(tuple(range(8))))
        self.assertEqual(len(pairings), 105)
        self.assertEqual(len(set(pairings)), 105)
        for pairing in pairings:
            monomial = contraction_from_pairing(pairing)
            self.assertTrue(monomial.is_complete_contraction())

    def test_bianchi_relation_is_generated_not_assumed_as_slot_symmetry(self) -> None:
        monomial = TensorMonomial(
            (
                TensorFactor(RIEMANN, (0, 1, 2, 3)),
                TensorFactor(RIEMANN, (0, 1, 2, 3)),
            )
        )
        self.assertTrue(bianchi_relation(monomial, 0))

    def test_exact_bianchi_quotient_derives_three_classes(self) -> None:
        analysis = quadratic_curvature_analysis()
        self.assertEqual(analysis["raw_pairing_count"], 105)
        self.assertEqual(analysis["symmetry_canonical_monomial_count"], 4)
        self.assertEqual(analysis["bianchi_relation_rank"], 1)
        self.assertEqual(analysis["quotient_dimension"], 3)
        self.assertEqual(analysis["named_representative_rank"], 3)
        self.assertEqual(
            analysis["named_representatives"],
            ("Riemann_squared", "Ricci_squared", "scalar_curvature_squared"),
        )

    def test_analysis_is_deterministic_in_process(self) -> None:
        first = quadratic_curvature_analysis()
        second = quadratic_curvature_analysis()
        for key in (
            "raw_pairing_count",
            "symmetry_canonical_monomial_count",
            "nonzero_unique_bianchi_relation_count",
            "bianchi_relation_rank",
            "quotient_dimension",
            "named_representative_rank",
        ):
            self.assertEqual(first[key], second[key])


if __name__ == "__main__":
    unittest.main()
