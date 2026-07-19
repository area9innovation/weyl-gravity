from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.generic_scalar_triangle_differential_system import (
    OUTPUT,
    SCHEMA,
    validate,
)
from spectral.euclidean.verify_generic_scalar_triangle_differential_system import verify


class GenericScalarTriangleDifferentialSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_independent_exact_verifier(self) -> None:
        verify()

    def test_system_and_boundary(self) -> None:
        flags = self.value["claim_flags"]
        self.assertTrue(flags["SCALAR_TRIANGLE_DIFFERENTIAL_SYSTEM_COMPUTED"])
        self.assertTrue(flags["TWO_LOG_MASTER_REDUCTION_COMPUTED"])
        self.assertTrue(flags["EQUAL_WEIGHT_CORNER_ANGULAR_SUM_COMPUTED"])
        self.assertFalse(flags["GHOST_CHANNEL_FUNCTIONS_COMPUTED"])
        self.assertFalse(flags["I29_POLE4_REDUCED"])

    def test_schema_rejects_promotion(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["I29_POLE4_REDUCED"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutant)

    def test_digest_rejects_mutation(self) -> None:
        mutant = deepcopy(self.value)
        mutant["master_rows"]["M_x1"]["J_triangle"]["numerator_terms"][0]["coefficient"]["numerator"] += 1
        with self.assertRaises(ValueError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
