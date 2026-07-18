from __future__ import annotations

from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.generic_background_ghost_schur_weight_raised_zeta_factorization import (
    OUTPUT,
    SCHEMA,
    build,
)
from spectral.euclidean.verify_generic_background_ghost_schur_weight_raised_zeta_factorization import (
    verify as independent_verify,
)


class GenericBackgroundGhostSchurWeightRaisedZetaFactorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_exact_generic_local_defect(self) -> None:
        result = self.value["generic_local_result"]
        self.assertEqual(
            result["coefficient_of_(4pi)^-2_integral_R2"],
            {"numerator": -1, "denominator": 108},
        )
        self.assertEqual(
            result["coefficient_of_(4pi)^-2_integral_Ric2"],
            {"numerator": -1, "denominator": 54},
        )
        self.assertEqual(-Fraction(1, 4) * Fraction(1, 27), Fraction(-1, 108))

    def test_bch_filtration_and_weighted_trace_cancellation(self) -> None:
        bch = self.value["BCH_reduction"]
        self.assertEqual(bch["orders"]["[X,Y]"], -3)
        self.assertEqual(bch["orders"]["[Y,[Y,X]]"], -4)
        self.assertEqual(bch["orders"]["[X,[X,Y]]"], -6)
        self.assertEqual(
            bch["weighted_BCH_trace_through_residue_order"],
            {"numerator": 0, "denominator": 1},
        )

    def test_round_specialization_and_convention_crosswalk(self) -> None:
        self.assertEqual(
            self.value["round_S4_crosscheck"]["weight_raised_defect"],
            {"numerator": -1, "denominator": 3},
        )
        self.assertEqual(
            self.value["factorization_convention_crosswalk"]["difference_of_defects"],
            {"numerator": 2, "denominator": 1},
        )
        self.assertIn(
            "not contradictory",
            self.value["factorization_convention_crosswalk"]["explanation"],
        )

    def test_claim_boundary(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["GENERIC_WEIGHT_RAISED_SCHUR_ZETA_FACTORIZATION_DEFECT_COMPUTED"])
        self.assertFalse(flags["GENERIC_BACKGROUND_FINITE_SCHUR_ROWS_COMPUTED"])
        self.assertFalse(flags["FULL_GHOST_BLOCK_ZETA_FACTORIZATION_COMPUTED"])
        self.assertFalse(flags["PHYSICAL_FOURTH_ORDER_HESSIAN_KERNEL_COMPUTED"])
        self.assertFalse(flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_independent_verifier(self) -> None:
        result = independent_verify()
        self.assertTrue(result["direct_round_ratio"].startswith("-4.311478818948"))


if __name__ == "__main__":
    unittest.main()
