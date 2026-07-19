from __future__ import annotations

from copy import deepcopy
import unittest

from spectral.euclidean.generic_background_physical_hessian_linear_curvature import build, validate
from spectral.euclidean.verify_generic_background_physical_hessian_linear_curvature import verify


class GenericBackgroundPhysicalHessianLinearCurvatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_same_gauge_and_repository_normalization(self) -> None:
        self.assertTrue(self.value["gauge_crosswalk"]["same_gauge"])
        self.assertEqual(
            self.value["repository_normalization"]["repository_functional_Hessian"],
            "H_repository=(1/2)H_source",
        )
        self.assertEqual(
            self.value["repository_normalization"]["flat_TT_leading_coefficient"],
            {"numerator": 1, "denominator": 2},
        )

    def test_complete_linear_source_rows_and_scalar_flat_slice(self) -> None:
        rows = self.value["source_operator"]["coefficient_rows"]
        self.assertEqual([len(rows[name]) for name in ("V_rho_sigma", "N_lambda", "U")], [9, 8, 5])
        self.assertEqual(
            self.value["scalar_flat_restriction"]["surviving_term_counts"],
            {"V_rho_sigma": 7, "N_lambda": 6, "U": 3},
        )

    def test_round_s4_remainder_keeps_full_hessian_open(self) -> None:
        check = self.value["round_S4_linear_crosscheck"]
        self.assertEqual(check["source_linear_operator"], "A^2+6 K A with A=-Box")
        self.assertIn("+8 K^2", check["missing_curvature_squared_fixture"])
        self.assertFalse(self.value["claim_flags"]["FULL_GENERIC_PHYSICAL_HESSIAN_SUPPLIED"])

    def test_only_three_linear_insertion_gate_opens(self) -> None:
        self.assertTrue(
            self.value["claim_flags"]["PHYSICAL_N3_THREE_LINEAR_INSERTION_VERTEX_READY"]
        )
        self.assertFalse(self.value["claim_flags"]["PHYSICAL_N3_TRIANGLE_INTEGRATED"])
        self.assertFalse(
            self.value["claim_flags"]["PHYSICAL_MIXED_N1_N2_THIRD_CURVATURE_ROWS_COMPUTED"]
        )

    def test_gauge_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["gauge_crosswalk"]["source_parameters"]["tau"] = {
            "numerator": 0,
            "denominator": 1,
        }
        with self.assertRaises(Exception):
            verify(mutant)

    def test_formula_mutation_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["source_operator"]["coefficient_rows"]["V_rho_sigma"][0][
            "coefficient"
        ] = {"numerator": -1, "denominator": 3}
        with self.assertRaises(Exception):
            verify(mutant)

    def test_full_hessian_overclaim_is_rejected(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["FULL_GENERIC_PHYSICAL_HESSIAN_SUPPLIED"] = True
        with self.assertRaises(Exception):
            validate(mutant)

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify(), self.value)


if __name__ == "__main__":
    unittest.main()
