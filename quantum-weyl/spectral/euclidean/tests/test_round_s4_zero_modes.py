from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.round_s4_zero_modes import (
    OUTPUT,
    SCHEMA,
    build,
    factor_spectrum,
    scalar_degeneracy,
    transverse_vector_degeneracy,
    validate_claim_boundary,
)
from spectral.euclidean.verify_round_s4_zero_modes import verify


class RoundS4ZeroModeTests(unittest.TestCase):
    def test_ghost_zero_levels_and_degeneracies(self) -> None:
        self.assertEqual(factor_spectrum(0, -4, 0)["zero_levels"], [1])
        self.assertEqual(factor_spectrum(1, -3, 1)["zero_levels"], [1])
        self.assertEqual(scalar_degeneracy(1), 5)
        self.assertEqual(transverse_vector_degeneracy(1), 10)

    def test_physical_tt_factors_have_no_zero_modes(self) -> None:
        self.assertEqual(factor_spectrum(2, 2, 2)["zero_levels"], [])
        self.assertEqual(factor_spectrum(2, 4, 2)["zero_levels"], [])

    def test_claim_boundary_rejects_repository_promotion(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["REPOSITORY_GLOBAL_ZERO_MODE_LEDGER_COMPLETE"] = True
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
