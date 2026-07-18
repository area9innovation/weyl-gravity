from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.york_hodge_berezinian import (
    OUTPUT,
    SCHEMA,
    build,
    measure_exponent_ledger,
    quartet_superdet_identity,
    validate_claim_boundary,
    york_gram_identity,
)
from spectral.euclidean.verify_york_hodge_berezinian import verify


def as_fraction(value: dict[str, int]) -> Fraction:
    return Fraction(value["numerator"], value["denominator"])


class YorkHodgeBerezinianTests(unittest.TestCase):
    def test_york_shifts_are_forced_by_dimension_four(self) -> None:
        identity = york_gram_identity()
        self.assertTrue(identity["verified_4d_target"])
        self.assertEqual(as_fraction(identity["vector_operator_R_shift"]), Fraction(1, 4))
        self.assertEqual(as_fraction(identity["scalar_norm_prefactor"]), Fraction(3, 4))
        self.assertEqual(as_fraction(identity["scalar_operator_R_shift"]), Fraction(1, 3))
        self.assertFalse(york_gram_identity(dimension=5)["verified_4d_target"])

    def test_hodge_delta_factor_cancels(self) -> None:
        ledger = measure_exponent_ledger()
        self.assertTrue(ledger["verified"])
        self.assertEqual(as_fraction(ledger["totals"]["Delta_0"]), 0)
        self.assertEqual(as_fraction(ledger["totals"]["Delta_1_T-R/4"]), Fraction(1, 2))
        self.assertEqual(as_fraction(ledger["totals"]["Delta_0-R/3"]), Fraction(1, 2))

    def test_quartet_superdeterminant_is_one(self) -> None:
        identity = quartet_superdet_identity()
        self.assertTrue(identity["verified"])
        self.assertEqual(as_fraction(identity["total_det_M_exponent"]), 0)

    def test_multiplier_hodge_mutation_is_rejected(self) -> None:
        mutant = measure_exponent_ledger(include_multiplier_hodge=False)
        self.assertFalse(mutant["verified"])
        self.assertEqual(as_fraction(mutant["totals"]["Delta_0"]), Fraction(-1, 2))

    def test_claim_boundary_rejects_zero_mode_promotion(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["GLOBAL_ZERO_MODE_LEDGER_COMPLETE"] = True
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
