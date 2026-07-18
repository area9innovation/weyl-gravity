from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.auxiliary_contour_phase import (
    OUTPUT,
    SCHEMA,
    build,
    convergence_wedge,
    modewise_completion,
    validate_claim_boundary,
)
from spectral.euclidean.verify_auxiliary_contour_phase import verify


class AuxiliaryContourPhaseTests(unittest.TestCase):
    def test_positive_imaginary_thimble_completes_square(self) -> None:
        result = modewise_completion()
        self.assertTrue(result["completion_verified"])
        self.assertTrue(result["rotated_quadratic_real_part_positive"])

    def test_wrong_sign_and_real_axis_are_rejected(self) -> None:
        self.assertFalse(modewise_completion(auxiliary_sign=1)["completion_verified"])
        self.assertFalse(convergence_wedge(0)["absolutely_convergent"])

    def test_claim_boundary_rejects_repository_promotion(self) -> None:
        mutant = deepcopy(build())
        mutant["claim_flags"]["REPOSITORY_AUXILIARY_CONTOUR_MATCHED"] = True
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
