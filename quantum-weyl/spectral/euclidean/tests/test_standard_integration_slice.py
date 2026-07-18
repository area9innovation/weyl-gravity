from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.standard_integration_slice import (
    OUTPUT,
    SCHEMA,
    build,
    factor_exponent_ledger,
    validate_claim_boundary,
)
from spectral.euclidean.verify_standard_integration_slice import verify


def as_fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class StandardIntegrationSliceTests(unittest.TestCase):
    def test_gamma_and_partition_exponents_are_opposite(self) -> None:
        for row in factor_exponent_ledger():
            self.assertEqual(as_fraction(row["Gamma_logdet_exponent"]), -as_fraction(row["Z_determinant_exponent"]))

    def test_standard_zero_mode_total_is_fifteen(self) -> None:
        self.assertEqual(sum(row["zero_mode_dimension"] for row in factor_exponent_ledger()), 15)
        self.assertEqual(sum(row["zero_mode_dimension"] for row in factor_exponent_ledger(ghost_scalar_zero_modes=4)), 14)

    def test_claim_boundary_rejects_repository_promotion(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["REPOSITORY_ANOMALY_COEFFICIENT_COMPUTED"] = True
        with self.assertRaisesRegex(ValueError, "claim boundary"):
            validate_claim_boundary(mutant)

    def test_schema_and_independent_verifier(self) -> None:
        value = build()
        self.assertEqual(json.loads(OUTPUT.read_text()), value)
        self.assertEqual(verify(), value)
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(value)
        mutant = deepcopy(value)
        mutant["claim_flags"]["QME_DISPOSITION"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
