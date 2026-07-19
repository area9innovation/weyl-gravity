from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.product_s2_s2_ghost_schur_det3_enclosure import (
    OUTPUT,
    SCHEMA,
    _k_fraction,
    build,
)
from spectral.euclidean.verify_product_s2_s2_ghost_schur_det3_enclosure import (
    main as independent_verify,
)


def _q(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class ProductS2S2GhostSchurDet3EnclosureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_positive_regular_k_and_large_mode_inventory(self) -> None:
        self.assertEqual(_k_fraction(1, 1), Fraction(1, 2))
        self.assertEqual(_k_fraction(2, 1), Fraction(5, 36))
        enclosure = self.value["det3_enclosure"]
        self.assertEqual(enclosure["large_mode_count"], 54)
        self.assertEqual(enclosure["large_K_threshold"], {"numerator": 1, "denominator": 100})

    def test_enclosure_is_nonempty_and_coefficient_bearing(self) -> None:
        enclosure = self.value["det3_enclosure"]
        lower = Decimal(enclosure["lower_endpoint_decimal"])
        upper = Decimal(enclosure["upper_endpoint_decimal"])
        self.assertLess(lower, upper)
        self.assertLess(upper - lower, Decimal("5.2e-8"))
        self.assertTrue(enclosure["certified_common_decimal_prefix"].startswith("0.3263039"))
        proof = enclosure["binary64_rounding_proof"]
        self.assertLess(
            Fraction(**proof["derived_absolute_rounding_bound"]),
            Fraction(**proof["declared_cushion"]),
        )

    def test_fail_closed_weighted_rows(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["PRODUCT_REGULAR_COMPLEMENT_DET3_VALUE_COMPUTED"])
        self.assertTrue(flags["MATCHED_EXCEPTIONAL_CORRECTION_RETAINED"])
        self.assertFalse(flags["PRODUCT_WEIGHTED_R_K_COMPUTED"])
        self.assertFalse(flags["PRODUCT_FINITE_PART_R_K2_COMPUTED"])
        self.assertFalse(flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
