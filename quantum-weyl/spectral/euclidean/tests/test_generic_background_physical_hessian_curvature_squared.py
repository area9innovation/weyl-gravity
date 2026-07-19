from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import unittest

from spectral.euclidean.generic_background_physical_hessian_curvature_squared import build, validate
from spectral.euclidean.verify_generic_background_physical_hessian_curvature_squared import verify


class GenericBackgroundPhysicalHessianCurvatureSquaredTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_projected_monic_h2_rows(self) -> None:
        rows = self.value["source_operator"]["coefficient_rows"]
        self.assertEqual(len(rows), 18)
        self.assertEqual(sum(row["tracefree_null"] for row in rows), 6)
        self.assertEqual(sum(row["source_cancellation"] for row in rows), 1)

    def test_gauge_ordering_only_changes_h1(self) -> None:
        gauge = self.value["gauge_ordering_crosswalk"]
        for fixture in gauge["exact_fixture_ledger"]:
            self.assertEqual(
                fixture["repository_minus_source"]["numerator"]
                * fixture["G_Ric"]["denominator"],
                2
                * fixture["G_Ric"]["numerator"]
                * fixture["repository_minus_source"]["denominator"],
            )
        self.assertTrue(
            self.value["claim_flags"]["GAUGE_ORDERING_DOES_NOT_CHANGE_ALGEBRAIC_H2"]
        )

    def test_scalar_flat_vertex_ready(self) -> None:
        restriction = self.value["scalar_flat_restriction"]
        self.assertEqual(restriction["effective_term_count"], 9)
        self.assertTrue(restriction["algebraic_H2_complete_on_declared_domain"])

    def test_round_s4_separates_u2_from_h1_commutator(self) -> None:
        check = self.value["round_S4_crosscheck"]
        self.assertEqual(check["algebraic_U2_on_TT"], "+24 K^2 identity")
        self.assertEqual(
            sum(
                Fraction(
                    row["coefficient"]["numerator"],
                    row["coefficient"]["denominator"],
                )
                for row in check["source_W_term_contributions_to_TT_eigenvalue"]
            ),
            Fraction(24),
        )
        self.assertEqual(check["linear_block_commutator_contribution_at_order_K2"], "-16 K^2 identity")
        self.assertEqual(check["sum"], "+24 K^2-16 K^2=+8 K^2")

    def test_mixed_trace_stays_open(self) -> None:
        self.assertFalse(self.value["claim_flags"]["PHYSICAL_MIXED_H1_H2_TRACE_COMPUTED"])
        self.assertFalse(self.value["claim_flags"]["PHYSICAL_M14_CORNER_CLASS_DISPOSED"])

    def test_h2_overclaim_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["PHYSICAL_MIXED_H1_H2_TRACE_COMPUTED"] = True
        with self.assertRaises(Exception):
            validate(mutant)

    def test_source_coefficient_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["source_operator"]["coefficient_rows"][0]["coefficient"] = {
            "numerator": 2,
            "denominator": 1,
        }
        with self.assertRaises(Exception):
            verify(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(self.value), self.value)


if __name__ == "__main__":
    unittest.main()
