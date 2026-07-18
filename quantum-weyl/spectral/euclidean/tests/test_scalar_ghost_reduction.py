from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.scalar_ghost_reduction import (
    OUTPUT,
    SCHEMA,
    build,
    scalar_fp_identity,
    validate_claim_boundary,
)
from spectral.euclidean.verify_scalar_ghost_reduction import verify


class ScalarGhostReductionTests(unittest.TestCase):
    def test_canonical_block_is_triangular_and_rank_one(self) -> None:
        identity = scalar_fp_identity()
        self.assertTrue(identity["triangular"])
        self.assertTrue(identity["verified"])
        self.assertEqual(identity["proportionality_constant"], -12)
        self.assertEqual(identity["target_residual"], [])

    def test_determinant_is_beta_independent(self) -> None:
        determinants = {
            json.dumps(scalar_fp_identity(beta=beta)["determinant"], sort_keys=True)
            for beta in (Fraction(0), Fraction(1, 4), Fraction(1, 2), Fraction(1))
        }
        self.assertEqual(len(determinants), 1)
        self.assertFalse(scalar_fp_identity(beta=Fraction(0))["triangular"])

    def test_ricci_commutator_mutation_is_rejected(self) -> None:
        mutant = scalar_fp_identity(ricci_pair_coefficient=Fraction(1, 4))
        self.assertFalse(mutant["verified"])
        self.assertNotEqual(mutant["target_residual"], [])

    def test_claim_boundary_rejects_qme_promotion(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["QME_DISPOSITION"] = True
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
        mutant["target_match"]["differential_output_factor_rank"] = 2
        with self.assertRaises(ValidationError):
            Draft202012Validator(schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
