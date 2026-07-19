from __future__ import annotations

from decimal import Decimal, localcontext
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator
import mpmath as mp
from mpmath.libmp import to_rational

from spectral.euclidean.product_s2_s2_ghost_minimal_vector_determinant_precertificate import (
    OUTPUT,
    SCHEMA,
    _endpoint,
    build,
)
from spectral.euclidean.verify_product_s2_s2_ghost_minimal_vector_determinant_precertificate import main as independent_verify


class ProductS2S2GhostMinimalVectorDeterminantPrecertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_full_weighted_enclosure_contains_candidate(self) -> None:
        row = self.value["directed_enclosures"]["full_vector_plus_schur_weighted"]
        self.assertLess(Decimal(row["lower"]), Decimal("19.0791630"))
        self.assertGreater(Decimal(row["upper"]), Decimal("19.0791630"))
        self.assertLess(Decimal(row["upper"]) - Decimal(row["lower"]), Decimal("3.3e-6"))

    def test_serialized_interval_endpoints_round_outward(self) -> None:
        mp.iv.dps = 70
        interval = mp.iv.mpf(2) / 7
        exact_lower = Fraction(*to_rational(interval._mpi_[0]))
        exact_upper = Fraction(*to_rational(interval._mpi_[1]))
        self.assertLessEqual(Fraction(_endpoint(interval, 0)), exact_lower)
        self.assertGreaterEqual(Fraction(_endpoint(interval, 1)), exact_upper)

    def test_zeta_weighted_defect_is_exactly_minus_ten(self) -> None:
        rows = self.value["directed_enclosures"]
        with localcontext() as context:
            context.prec = 100
            for endpoint in ("lower", "upper"):
                self.assertEqual(
                    Decimal(rows["two_polarization_minimal_vector_weighted"][endpoint]) - 10,
                    Decimal(rows["two_polarization_minimal_vector_zeta"][endpoint]),
                )

    def test_special_background_claims_are_promoted_and_scoped(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["FULL_VECTOR_PLUS_SCHUR_WEIGHTED_ENCLOSURE_DERIVED"])
        self.assertTrue(flags["MINIMAL_VECTOR_INFINITE_WEIGHTED_DETERMINANT_COMPUTED"])
        self.assertTrue(flags["FULL_COUPLED_VECTOR_SCHUR_DETERMINANT_COMPUTED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])
        self.assertEqual(self.value["tier3_promotion_receipt"]["status"], "PASSED")

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
