from __future__ import annotations

from copy import deepcopy
import unittest

from spectral.euclidean.generic_background_ghost_cpt_obstruction import build, validate
from spectral.euclidean.verify_generic_background_ghost_cpt_obstruction import verify


class GenericBackgroundGhostCptObstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schur_operator_is_beta_independent(self) -> None:
        rows = self.value["algebraic_Weyl_ghost_elimination"]["beta_controls"]
        self.assertEqual(
            [row["effective_divergence_coefficient"] for row in rows],
            [{"numerator": 1, "denominator": 2}] * 3,
        )

    def test_principal_symbol_is_elliptic_but_nonminimal(self) -> None:
        symbol = self.value["nonminimal_principal_symbol"]
        self.assertTrue(symbol["elliptic"])
        self.assertFalse(symbol["Laplace_type"])
        self.assertEqual(symbol["characteristic_polynomial"], "(lambda-1)^3(lambda-3/2)")

    def test_generic_hodge_split_fails_but_einstein_factor_returns(self) -> None:
        hodge = self.value["generic_Hodge_mixing"]
        self.assertFalse(hodge["longitudinal_subspace_preserved"])
        self.assertEqual(hodge["transverse_mixing_term_2S_dot_k"], [0, 2, 0, 0])
        self.assertEqual(hodge["Einstein_scalar_factor_reproduced"], "Delta_0-R/3")

    def test_minimal_cpt_promotion_is_refused(self) -> None:
        self.assertEqual(
            self.value["CPT_applicability_decision"]["verdict"],
            "DIRECT_MINIMAL_CPT_SUBSTITUTION_FOR_THE_GENERIC_GHOST_SECTOR_IS_OBSTRUCTED",
        )
        self.assertFalse(self.value["claim_flags"]["GENERIC_NONMINIMAL_GHOST_CPT_DETERMINANT_COMPUTED"])

    def test_overclaim_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["REPOSITORY_CUBIC_COEFFICIENTS_COMPUTED"] = True
        with self.assertRaises(Exception):
            validate(mutant)

    def test_formula_mutation_is_rejected_independently(self) -> None:
        mutant = deepcopy(self.value)
        mutant["algebraic_Weyl_ghost_elimination"]["beta_controls"][0][
            "effective_divergence_coefficient"
        ] = {"numerator": 1, "denominator": 1}
        with self.assertRaises(Exception):
            verify(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.value)


if __name__ == "__main__":
    unittest.main()
