from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.product_s2_s2_ghost_schur_weighted_rows import (
    OUTPUT,
    SCHEMA,
    build,
)
from spectral.euclidean.verify_product_s2_s2_ghost_schur_weighted_rows import (
    main as independent_verify,
)


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class ProductS2S2GhostSchurWeightedRowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_uniform_heat_remainder_is_small(self) -> None:
        proof = self.value["euler_maclaurin_remainder_proof"]
        self.assertEqual(proof["order"], 18)
        self.assertLess(_q(proof["row_R_K_error_bound"]), Fraction(22, 10**13))
        self.assertLess(_q(proof["row_FP_R_K2_error_bound"]), Fraction(9, 10**13))

    def test_weighted_row_enclosures(self) -> None:
        rows = self.value["weighted_rows"]
        for name in ("R_Delta_K", "FP_R_Delta_K2", "low_order_split_R_K_minus_half_R_K2"):
            lower = Decimal(rows[name]["lower"])
            upper = Decimal(rows[name]["upper"])
            self.assertLess(lower, upper)
            self.assertLess(upper - lower, Decimal("4e-9"))

    def test_claim_promotion_is_scoped(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["PRODUCT_WEIGHTED_ROW_RIGOROUS_ENCLOSURES_DERIVED"])
        self.assertTrue(flags["PRODUCT_HEAT_EULER_MACLAURIN_REMAINDER_RIGOROUSLY_BOUNDED"])
        self.assertFalse(flags["PRODUCT_WEIGHTED_R_K_COMPUTED"])
        self.assertFalse(flags["PRODUCT_FINITE_PART_R_K2_COMPUTED"])
        self.assertFalse(flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"])
        self.assertFalse(flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
