from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.generic_background_physical_hessian_mellin_subtraction_scale_row import build


HERE = Path(__file__).resolve().parents[1]


class PhysicalHessianMellinSubtractionScaleRowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build()
        cls.schema = json.loads((HERE / "schema/generic-background-physical-hessian-mellin-subtraction-scale-row-v1.schema.json").read_text())

    def test_schema(self) -> None:
        Draft202012Validator(self.schema).validate(self.payload)

    def test_exact_scale_row(self) -> None:
        self.assertEqual(
            self.payload["renormalization_scale_row"]["coefficient"],
            {"numerator": 15707, "denominator": 216},
        )

    def test_fail_closed_boundary(self) -> None:
        flags = self.payload["claim_flags"]
        self.assertTrue(flags["FIXTURE_MINIMAL_SUBTRACTION_DISTRIBUTION_FIXED"])
        self.assertFalse(flags["GENERIC_COVARIANT_VOLTERRA_LIFT_COMPUTED"])
        self.assertFalse(flags["PHYSICAL_M14_CORNER_CLASS_DISPOSED"])

    def test_mutation_rejected(self) -> None:
        mutant = copy.deepcopy(self.payload)
        mutant["renormalization_scale_row"]["coefficient"]["numerator"] += 1
        with self.assertRaises(ValidationError):
            Draft202012Validator(self.schema).validate(mutant)


if __name__ == "__main__":
    unittest.main()
