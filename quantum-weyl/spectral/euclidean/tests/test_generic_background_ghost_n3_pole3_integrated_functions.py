from __future__ import annotations

from copy import deepcopy
import json
import unittest

from jsonschema import Draft202012Validator, ValidationError

from spectral.euclidean.generic_background_ghost_n3_pole3_integrated_functions import (
    OUTPUT,
    SCHEMA,
    validate,
)
from spectral.euclidean.verify_generic_background_ghost_n3_pole3_integrated_functions import verify


class GenericGhostN3PoleThreeIntegratedFunctionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.value = json.loads(OUTPUT.read_text())

    def test_independent_exact_verifier(self) -> None:
        verify()

    def test_ten_functions_and_boundary(self) -> None:
        flags = self.value["claim_flags"]
        self.assertEqual(len(self.value["channel_rows"]), 10)
        self.assertTrue(flags["TEN_POLE3_GENERIC_INTEGRATED_FUNCTIONS_COMPUTED"])
        self.assertTrue(flags["CORNER_ANGULAR_FLUXES_EVALUATED"])
        self.assertTrue(flags["TWO_BUBBLE_LOG_RATIOS_EXPLICIT"])
        self.assertFalse(flags["I29_POLE4_REDUCED"])
        self.assertFalse(flags["ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED"])

    def test_all_symmetric_regressions_and_i28_relation(self) -> None:
        self.assertEqual(
            self.value["identity_ledger"]["symmetric_point_regression_status"],
            "ALL_EXACT_MATCH",
        )
        self.assertTrue(
            all(
                value == "ZERO"
                for value in self.value["identity_ledger"]["I28_basis_coordinate_defects"].values()
            )
        )

    def test_schema_rejects_promotion(self) -> None:
        mutant = deepcopy(self.value)
        mutant["claim_flags"]["ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED"] = True
        with self.assertRaises(ValidationError):
            Draft202012Validator(json.loads(SCHEMA.read_text())).validate(mutant)

    def test_digest_rejects_mutation(self) -> None:
        mutant = deepcopy(self.value)
        mutant["channel_rows"][0]["function_basis_coordinates"]["rational_corner"]["numerator_terms"][0]["coefficient"]["numerator"] += 1
        with self.assertRaises(ValueError):
            validate(mutant)


if __name__ == "__main__":
    unittest.main()
