from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator
import mpmath as mp
from mpmath.libmp import to_rational

from spectral.euclidean.product_s2_s2_ghost_schur_modified_determinant_precertificate import (
    OUTPUT,
    SCHEMA,
    _endpoint,
    build,
)
from spectral.euclidean.verify_product_s2_s2_ghost_schur_modified_determinant_precertificate import main as independent_verify


class ProductS2S2GhostSchurModifiedDeterminantPrecertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_interval_assembly(self) -> None:
        rows = self.value["directed_enclosures"]
        regular = rows["regular_modified_determinant"]
        coupled = rows["coupled_schur_log"]
        self.assertLess(Decimal(regular["lower"]), Decimal("-2.89784225"))
        self.assertGreater(Decimal(regular["upper"]), Decimal("-2.89784225"))
        self.assertLess(Decimal(coupled["lower"]), Decimal("-9.48951598"))
        self.assertGreater(Decimal(coupled["upper"]), Decimal("-9.48951598"))

    def test_serialized_interval_endpoints_round_outward(self) -> None:
        mp.iv.dps = 70
        interval = -mp.iv.mpf(1) / 3
        exact_lower = Fraction(*to_rational(interval._mpi_[0]))
        exact_upper = Fraction(*to_rational(interval._mpi_[1]))
        self.assertLessEqual(Fraction(_endpoint(interval, 0)), exact_lower)
        self.assertGreaterEqual(Fraction(_endpoint(interval, 1)), exact_upper)

    def test_tier3_promotion_and_full_vector_boundary(self) -> None:
        self.assertEqual(self.value["tier3_promotion_receipt"]["status"], "PASSED")
        self.assertEqual(self.value["tier3_promotion_receipt"]["tests_run"], 850)
        flags = self.value["claim_flags"]
        self.assertTrue(flags["MATCHED_EXCEPTIONAL_COUPLED_SCHUR_ENCLOSURE_DERIVED"])
        self.assertTrue(flags["PRODUCT_WEIGHTED_R_K_COMPUTED"])
        self.assertTrue(flags["PRODUCT_FINITE_PART_R_K2_COMPUTED"])
        self.assertFalse(flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
