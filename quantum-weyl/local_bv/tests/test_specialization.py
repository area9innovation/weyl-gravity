import unittest
from fractions import Fraction

from local_bv.curvature import EPSILON, RIEMANN
from local_bv.hodge import Signature
from local_bv.quotient import exact_nullspace
from local_bv.specialization import (
    RelationFamily,
    SpecializationTower,
    TensorOccurrence,
    WEYL,
    antisymmetrize_occurrences,
    epsilon_pair_expansion,
    reduce_epsilon_pair_in_monomial,
    replace_riemann_by_weyl,
    schouten_antisymmetrization,
)
from local_bv.tensors import TensorExpression, TensorFactor, TensorMonomial, TensorSpec


class SpecializationFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        even_specs = [
            TensorSpec.without_slot_symmetry(f"even_{index}", 0)
            for index in range(3)
        ]
        odd_spec = TensorSpec.without_slot_symmetry(
            "odd", 0, spacetime_parity=1
        )
        self.basis = tuple(
            TensorMonomial((TensorFactor(spec, ()),))
            for spec in (*even_specs, odd_spec)
        )

    def test_exact_nullspace_handles_empty_and_nontrivial_maps(self) -> None:
        self.assertEqual(
            exact_nullspace((), column_count=2),
            ((Fraction(1), Fraction(0)), (Fraction(0), Fraction(1))),
        )
        self.assertEqual(
            exact_nullspace(((1, 1, 0), (0, 1, 1))),
            ((Fraction(1), Fraction(-1), Fraction(1)),),
        )

    def test_stages_expose_surjective_maps_and_kernel_witnesses(self) -> None:
        universal_relation = TensorExpression(
            {self.basis[0]: 1, self.basis[1]: -1}
        )
        dimension_relation = TensorExpression(
            {self.basis[1]: 1, self.basis[2]: -1}
        )
        tower = SpecializationTower.start(
            "universal",
            self.basis,
            (
                RelationFamily(
                    "universal_symmetry",
                    (universal_relation,),
                    "generated witness",
                ),
            ),
        ).extend(
            "dimension_4",
            (
                RelationFamily(
                    "schouten_5_index",
                    (dimension_relation,),
                    "five-index antisymmetrization",
                    ("dimension=4",),
                ),
            ),
        )
        self.assertEqual([stage.dimension for stage in tower.stages], [3, 2])
        stage = tower.current
        self.assertEqual(len(stage.projection_kernel), 1)
        self.assertEqual(stage.parity_block_dimensions, {"even": 1, "odd": 1})
        for row in stage.projection_matrix:
            for witness in stage.projection_kernel:
                self.assertEqual(sum(a * b for a, b in zip(row, witness)), 0)
        payload = tower.canonical_payload()
        self.assertEqual(payload["stages"][1]["projection"]["rank"], 2)
        self.assertEqual(len(payload["tower_sha256"]), 64)

    def test_named_representative_coordinates_are_deterministic(self) -> None:
        tower = SpecializationTower.start("universal", self.basis)
        ledger = tower.current.representative_ledger(
            {
                "odd": TensorExpression.monomial(self.basis[3]),
                "zero": TensorExpression(),
            }
        )
        self.assertEqual(list(ledger), ["odd", "zero"])
        self.assertEqual(ledger["odd"]["status"], "NONZERO")
        self.assertEqual(ledger["zero"]["status"], "ZERO")

    def test_relation_families_reject_parity_mixing(self) -> None:
        mixed = TensorExpression({self.basis[0]: 1, self.basis[3]: 1})
        with self.assertRaisesRegex(ValueError, "fixed parity"):
            RelationFamily("bad", (mixed,), "invalid witness")

    def test_occurrence_antisymmetrizer_generates_five_index_primitive(self) -> None:
        generic = TensorSpec.without_slot_symmetry("generic_rank_5", 5)
        monomial = TensorMonomial(
            (TensorFactor(generic, (0, 1, 2, 3, 4)),)
        )
        occurrences = tuple(
            TensorOccurrence(0, "slots", index) for index in range(5)
        )
        relation = schouten_antisymmetrization(
            monomial,
            occurrences,
            dimension=4,
        )
        self.assertEqual(len(relation.terms), 120)
        first_swap = TensorMonomial(
            (TensorFactor(generic, (1, 0, 2, 3, 4)),)
        )
        swapped = antisymmetrize_occurrences(
            first_swap,
            tuple(TensorOccurrence(0, "slots", index) for index in range(5)),
        )
        self.assertEqual(swapped, -relation)
        with self.assertRaisesRegex(ValueError, r"dimension \+ 1"):
            schouten_antisymmetrization(
                monomial, occurrences[:-1], dimension=4
            )

    def test_tracefree_weyl_is_not_a_riemann_rename(self) -> None:
        traced = TensorExpression.monomial(
            TensorMonomial((TensorFactor(RIEMANN, (0, 1, 0, 1)),))
        )
        untraced = TensorExpression.monomial(
            TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
        )
        self.assertFalse(replace_riemann_by_weyl(traced))
        reduced = replace_riemann_by_weyl(untraced)
        self.assertTrue(reduced)
        self.assertTrue(
            all(
                factor.spec == WEYL
                for term in reduced.terms
                for factor in term.factors
            )
        )

    def test_derivative_riemann_to_weyl_shortcut_fails_closed(self) -> None:
        differentiated = TensorExpression.monomial(
            TensorMonomial(
                (TensorFactor(RIEMANN, (0, 1, 2, 3), (4,)),)
            )
        )
        with self.assertRaisesRegex(ValueError, "Schouten/Cotton"):
            replace_riemann_by_weyl(differentiated)

    def test_epsilon_pair_expansion_tracks_signature_and_parity(self) -> None:
        euclidean = epsilon_pair_expansion(Signature.EUCLIDEAN)
        lorentzian = epsilon_pair_expansion(Signature.LORENTZIAN)
        self.assertEqual(len(euclidean), 24)
        self.assertEqual(len({term.pairs for term in euclidean}), 24)
        self.assertEqual(
            [term.coefficient for term in lorentzian],
            [-term.coefficient for term in euclidean],
        )
        epsilon_square = TensorExpression.monomial(
            TensorMonomial(
                (
                    TensorFactor(EPSILON, (0, 1, 2, 3)),
                    TensorFactor(EPSILON, (0, 1, 2, 3)),
                )
            )
        )
        self.assertEqual(epsilon_square.parity_transform(), epsilon_square)
        euclidean_square = reduce_epsilon_pair_in_monomial(
            next(iter(epsilon_square.terms)), 0, 1, Signature.EUCLIDEAN
        )
        lorentzian_square = reduce_epsilon_pair_in_monomial(
            next(iter(epsilon_square.terms)), 0, 1, Signature.LORENTZIAN
        )
        scalar = TensorMonomial(())
        self.assertEqual(euclidean_square.terms[scalar], 24)
        self.assertEqual(lorentzian_square.terms[scalar], -24)


if __name__ == "__main__":
    unittest.main()
