import unittest

from local_bv.covariant_derivatives import covariant_commutator_relation_in_monomial
from local_bv.curvature import RIEMANN, pair_partitions
from local_bv.six_derivative import (
    commutator_relation_from_pairing,
    six_derivative_curvature_analysis,
)
from local_bv.tensors import TensorFactor, TensorMonomial


class SixDerivativeCurvatureTests(unittest.TestCase):
    def test_all_three_generated_sectors_are_joined(self) -> None:
        analysis = six_derivative_curvature_analysis()
        dimensions = analysis["sector_basis_dimensions_before_relations"]
        self.assertEqual(dimensions["R3"], 13)
        self.assertEqual(dimensions["nablaR_nablaR"], 12)
        self.assertEqual(dimensions["R_nabla2R"], 14)
        self.assertEqual(analysis["total_basis_dimension_before_relations"], 39)

    def test_ibp_and_commutator_relations_are_generated(self) -> None:
        analysis = six_derivative_curvature_analysis()
        counts = analysis["relation_counts"]
        self.assertGreater(counts["integration_by_parts"], 0)
        self.assertGreater(counts["covariant_commutators"], 0)
        for relation in analysis["relation_sets"]["integration_by_parts"]:
            self.assertTrue(all(term.is_complete_contraction() for term in relation.terms))
        for relation in analysis["relation_sets"]["covariant_commutators"]:
            self.assertTrue(all(term.is_complete_contraction() for term in relation.terms))

    def test_orbit_commutator_matches_direct_constructor(self) -> None:
        # Regression: forward and reversed terms can canonicalize to the same
        # monomial and must be added, not overwritten.
        cancelling = ((0, 2), (1, 4), (3, 5), (6, 8), (7, 9))
        self.assertFalse(commutator_relation_from_pairing(cancelling))

        for pairing in pair_partitions(tuple(range(10))):
            fast = commutator_relation_from_pairing(pairing)
            if not fast:
                continue
            labels = [0] * 10
            for label, (first, second) in enumerate(pairing):
                labels[first] = label
                labels[second] = label
            target = TensorFactor(RIEMANN, tuple(labels[2:6]))
            spectator = TensorFactor(RIEMANN, tuple(labels[6:10]))
            direct = covariant_commutator_relation_in_monomial(
                TensorMonomial((target, spectator)),
                0,
                labels[0],
                labels[1],
            )
            self.assertEqual(fast, direct)
            break
        else:
            self.fail("no nonzero contracted commutator witness was generated")

    def test_combined_quotient_has_exact_rank_dimension_identity(self) -> None:
        analysis = six_derivative_curvature_analysis()
        self.assertEqual(
            analysis["quotient_dimension"],
            analysis["total_basis_dimension_before_relations"]
            - analysis["combined_relation_rank"],
        )
        cumulative = analysis["cumulative_reduction"]
        dimensions = [item["quotient_dimension"] for item in cumulative.values()]
        self.assertEqual(dimensions, sorted(dimensions, reverse=True))
        self.assertEqual(analysis["combined_relation_rank"], 29)
        self.assertEqual(analysis["quotient_dimension"], 10)
        self.assertEqual(
            analysis["local_normal_form_before_total_derivatives"],
            {
                "relation_rank": 23,
                "quotient_dimension": 16,
                "omitted_degree_one_total_divergence_dimension": 1,
                "dimension_with_degree_one_sector": 17,
            },
        )
        self.assertEqual(
            analysis["final_sector_ranks"],
            {"R3": 8, "nablaR_nablaR": 4, "R_nabla2R": 4},
        )
        self.assertEqual(analysis["final_derivative_union_rank"], 4)
        self.assertEqual(analysis["derivative_classes_outside_cubic_span"], 2)


if __name__ == "__main__":
    unittest.main()
