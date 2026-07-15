import unittest

from local_bv.curvature import RIEMANN
from local_bv.hodge import Signature
from local_bv.specialization import WEYL
from local_bv.tensors import TensorExpression, TensorFactor, TensorMonomial
from local_bv.weyl_decomposition import (
    COTTON,
    cotton_cyclic_relation,
    cotton_definition_relation,
    differentiated_ricci_decomposition_relation,
    expand_cotton_definitions,
    expand_riemann_factors,
    hodge_dualize_weyl_factor,
    ricci_decomposition_relation,
    riemann_to_schouten_zero_weyl,
    schouten_zero_projection,
    tracefree_cotton_reduce,
    weyl_differential_bianchi_relation,
    weyl_hodge_square_contraction,
)


class WeylDecompositionTests(unittest.TestCase):
    def test_ricci_decomposition_and_derivative_are_explicit(self) -> None:
        relation = ricci_decomposition_relation()
        differentiated = differentiated_ricci_decomposition_relation()
        self.assertEqual(len(relation.terms), 6)
        self.assertEqual(len(differentiated.terms), 6)
        self.assertEqual(
            sum(
                any(factor.spec == RIEMANN for factor in monomial.factors)
                for monomial in differentiated.terms
            ),
            1,
        )
        self.assertEqual(
            sum(
                any(factor.spec == WEYL for factor in monomial.factors)
                for monomial in differentiated.terms
            ),
            1,
        )

    def test_riemann_expansion_is_derivative_safe(self) -> None:
        for expression, relation in (
            (
                TensorExpression.monomial(
                    TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
                ),
                ricci_decomposition_relation(),
            ),
            (
                TensorExpression.monomial(
                    TensorMonomial(
                        (TensorFactor(RIEMANN, (0, 1, 2, 3), (4,)),)
                    )
                ),
                differentiated_ricci_decomposition_relation(),
            ),
        ):
            expanded = expand_riemann_factors(expression)
            self.assertEqual(expression - expanded, relation)
            projected = riemann_to_schouten_zero_weyl(expression)
            self.assertTrue(projected)
            self.assertTrue(
                all(
                    factor.spec == WEYL
                    for monomial in projected.terms
                    for factor in monomial.factors
                )
            )
        with self.assertRaisesRegex(ValueError, "expand Riemann"):
            schouten_zero_projection(
                TensorExpression.monomial(
                    TensorMonomial((TensorFactor(RIEMANN, (0, 1, 2, 3)),))
                )
            )
        with self.assertRaisesRegex(ValueError, "multi-Riemann"):
            expand_riemann_factors(
                TensorExpression.monomial(
                    TensorMonomial(
                        (
                            TensorFactor(RIEMANN, (0, 1, 2, 3)),
                            TensorFactor(RIEMANN, (0, 1, 2, 3)),
                        )
                    )
                )
            )

    def test_cotton_convention_is_antisymmetric_cyclic_and_tracefree(self) -> None:
        definition = cotton_definition_relation()
        self.assertEqual(len(definition.terms), 3)
        self.assertFalse(expand_cotton_definitions(cotton_cyclic_relation()))
        for traced_slots in ((0, 0, 1), (0, 1, 0), (1, 0, 0)):
            traced = TensorExpression.monomial(
                TensorMonomial((TensorFactor(COTTON, traced_slots),))
            )
            self.assertFalse(tracefree_cotton_reduce(traced))

    def test_weyl_differential_bianchi_signs_follow_from_decomposition(self) -> None:
        # Cyclically differentiate R-W-g-wedge-P.  The differential Riemann
        # Bianchi row removes the R terms, leaving the negative of this sum.
        cyclic_decomposition = -(
            differentiated_ricci_decomposition_relation((0, 1, 2, 3), 4)
            + differentiated_ricci_decomposition_relation((1, 4, 2, 3), 0)
            + differentiated_ricci_decomposition_relation((4, 0, 2, 3), 1)
        )
        schouten_form = TensorExpression(
            {
                monomial: coefficient
                for monomial, coefficient in cyclic_decomposition.terms.items()
                if all(factor.spec != RIEMANN for factor in monomial.factors)
            }
        )
        cotton_form = expand_cotton_definitions(
            weyl_differential_bianchi_relation()
        )
        self.assertEqual(cotton_form, schouten_form)

    def test_full_weyl_hodge_dual_flips_parity(self) -> None:
        contraction = TensorMonomial(
            (
                TensorFactor(WEYL, (0, 1, 2, 3)),
                TensorFactor(WEYL, (0, 1, 2, 3)),
            )
        )
        dual = hodge_dualize_weyl_factor(contraction, 0)
        right_dual = hodge_dualize_weyl_factor(
            contraction, 0, pair="second"
        )
        self.assertTrue(dual)
        self.assertEqual(right_dual, dual)
        self.assertEqual(
            {monomial.spacetime_parity() for monomial in dual.terms}, {1}
        )
        self.assertEqual(dual.parity_transform(), -dual)
        with self.assertRaisesRegex(ValueError, "first.*second"):
            hodge_dualize_weyl_factor(contraction, 0, pair="invalid")

    def test_full_weyl_hodge_square_separates_signatures(self) -> None:
        contraction = TensorExpression.monomial(
            TensorMonomial(
                (
                    TensorFactor(WEYL, (0, 1, 2, 3)),
                    TensorFactor(WEYL, (0, 1, 2, 3)),
                )
            )
        )
        self.assertEqual(
            weyl_hodge_square_contraction(Signature.EUCLIDEAN), contraction
        )
        self.assertEqual(
            weyl_hodge_square_contraction(Signature.LORENTZIAN), -contraction
        )


if __name__ == "__main__":
    unittest.main()
