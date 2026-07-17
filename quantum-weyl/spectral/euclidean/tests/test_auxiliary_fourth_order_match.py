from __future__ import annotations

from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator

from spectral.euclidean.auxiliary_fourth_order_match import (
    OUTPUT,
    SCHEMA,
    build,
    schur_identity,
)
from spectral.euclidean.verify_auxiliary_fourth_order_match import verify


class AuxiliaryFourthOrderMatchTests(unittest.TestCase):
    def test_exact_block_determinant_and_schur_complement(self) -> None:
        identity = schur_identity()
        self.assertTrue(identity["verified"])
        self.assertEqual(identity["determinant_residual"], [])
        self.assertEqual(identity["schur_residual"], [])
        self.assertEqual(
            identity["fourth_order_target"],
            [
                {"degree": 1, "numerator": 2, "denominator": 1},
                {"degree": 2, "numerator": 1, "denominator": 1},
            ],
        )

    def test_wrong_top_left_block_is_rejected(self) -> None:
        mutant = schur_identity(top_left_shift=Fraction(3))
        self.assertFalse(mutant["verified"])
        self.assertEqual(
            mutant["determinant_residual"],
            [{"degree": 1, "numerator": -1, "denominator": 1}],
        )

    def test_repository_boundary_remains_open(self) -> None:
        value = build()
        flags = value["claim_flags"]
        self.assertTrue(flags["STANDARD_PHYSICAL_TT_AUXILIARY_SCHUR_IDENTITY"])
        self.assertTrue(flags["STANDARD_LOCAL_FIELD_DEPENDENT_JACOBIAN_ZERO"])
        self.assertFalse(flags["REPOSITORY_AUXILIARY_MEASURE_MATCH"])
        self.assertFalse(flags["REPOSITORY_ELLIPTIC_COMPLEX_CERTIFIED"])
        self.assertFalse(flags["QME_DISPOSITION"])

    def test_certificate_reproduces_validates_and_verifies(self) -> None:
        checked = json.loads(OUTPUT.read_text())
        self.assertEqual(checked, build())
        self.assertEqual(checked, verify())
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(checked)


if __name__ == "__main__":
    unittest.main()
