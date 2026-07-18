from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.tt_hessian_normalization_readiness import (
    OUTPUT,
    SCHEMA,
    build,
    curvature_identity,
    validate_claim_boundary,
)
from spectral.euclidean.verify_tt_hessian_normalization_readiness import verify


class TTHessianNormalizationReadinessTests(unittest.TestCase):
    def test_repository_curvature_identity_is_exact(self) -> None:
        self.assertTrue(curvature_identity()["verified"])

    def test_wrong_R_squared_coefficient_is_rejected(self) -> None:
        self.assertFalse(curvature_identity(scalar_coefficient=(1, 4))["verified"])

    def test_existing_backgrounds_do_not_promote_round_s4_match(self) -> None:
        value = build()
        self.assertFalse(value["claim_flags"]["REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED"])
        self.assertEqual(
            value["minimal_missing_carrier_theorem"]["missing_artifact"],
            "REPOSITORY_ROUND_S4_TT_HESSIAN_DICTIONARY_V1",
        )

    def test_claim_boundary_rejects_hessian_promotion(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["REPOSITORY_PHYSICAL_HESSIAN_NORMALIZED"] = True
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
