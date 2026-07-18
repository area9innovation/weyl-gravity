from __future__ import annotations

from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.round_s4_ghost_schur_zeta_factorization import (
    OUTPUT,
    SCHEMA,
    build,
)
from spectral.euclidean.verify_round_s4_ghost_schur_zeta_factorization import (
    main as independent_verify,
)


class RoundS4GhostSchurZetaFactorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = build()

    def test_schema_and_checked_in_certificate(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(self.value)
        self.assertEqual(self.value, json.loads(OUTPUT.read_text()))

    def test_exact_local_factorization_defect(self) -> None:
        derivation = self.value["local_residue_derivation"]
        self.assertEqual(derivation["Wres_Q_minus_2"], {"numerator": 1, "denominator": 3})
        self.assertEqual(
            derivation["exact_factorization_defect"],
            {"numerator": 5, "denominator": 3},
        )
        self.assertEqual(
            -Fraction(1, 4) * (4**2 - 6**2) * Fraction(1, 3),
            Fraction(5, 3),
        )

    def test_zeta_ratio_and_claim_boundary(self) -> None:
        result = self.value["factorization_result"]
        self.assertAlmostEqual(
            float(result["zeta_determinant_ratio_decimal"]),
            -2.311478818948745,
        )
        flags = self.value["claim_flags"]
        self.assertTrue(flags["ROUND_S4_ZETA_FACTORIZED_SCHUR_RATIO_COMPUTED"])
        self.assertFalse(flags["GENERIC_NONCOMMUTING_ZETA_FACTORIZATION_DEFECT_COMPUTED"])
        self.assertFalse(flags["GENERIC_BACKGROUND_FINITE_SCHUR_ROWS_COMPUTED"])

    def test_generic_gate_is_split(self) -> None:
        boundary = self.value["generic_boundary"]
        self.assertIn("BCH symbols", boundary["missing_local_carrier"])
        self.assertIn("Green kernel", boundary["missing_global_carrier"])
        self.assertIn("distinct gates", boundary["separation"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(independent_verify(), 0)


if __name__ == "__main__":
    unittest.main()
