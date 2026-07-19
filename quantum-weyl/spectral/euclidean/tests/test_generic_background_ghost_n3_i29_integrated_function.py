from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "certificates/GENERIC_BACKGROUND_GHOST_N3_I29_INTEGRATED_FUNCTION.json"
SCHEMA = HERE / "schema/generic-background-ghost-n3-i29-integrated-function-v1.schema.json"


class GenericBackgroundGhostN3I29IntegratedFunctionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = json.loads(CERTIFICATE.read_text())

    def test_strict_schema(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        Draft202012Validator.check_schema(schema)
        self.assertEqual(
            list(Draft202012Validator(schema).iter_errors(self.certificate)), []
        )

    def test_exact_rank_and_reconstruction_ledger(self) -> None:
        self.assertEqual(
            self.certificate["rank_ledger"],
            {
                "ambient_numerator_dimension": 55,
                "canonical_tangent_column_count": 46,
                "master_count": 3,
                "raw_tangent_column_count": 84,
                "tangent_plus_masters_and_target_rank": 49,
                "tangent_plus_masters_rank": 49,
                "tangent_rank": 46,
            },
        )
        reconstruction = self.certificate["exact_reconstruction"]
        self.assertEqual(reconstruction["lambda_denominator_power"], 5)
        self.assertEqual(reconstruction["master_numerator_degrees"], [7, 8, 8])
        self.assertEqual(reconstruction["interpolation_point_count"], 45)
        self.assertEqual(reconstruction["full_55_row_symbolic_relative_IBP_defect"], "ZERO")

    def test_corner_and_symmetric_regressions(self) -> None:
        self.assertEqual(
            self.certificate["corner_flux"]["corner_numerator_degrees"], [1, 1, 1]
        )
        identity = self.certificate["identity_ledger"]
        self.assertEqual(len(identity["S3_covariance"]), 6)
        self.assertEqual(identity["symmetric_point_J_coefficient"], {"numerator": -496, "denominator": 6561})
        self.assertEqual(identity["symmetric_point_rational_term"], {"numerator": 1160, "denominator": 6561})
        self.assertEqual(identity["symmetric_point_status"], "EXACT_MATCH")

    def test_claim_boundary(self) -> None:
        flags = self.certificate["claim_flags"]
        self.assertTrue(flags["I29_POLE4_REDUCED"])
        self.assertTrue(flags["ALL_ELEVEN_GENERIC_GHOST_N3_FUNCTIONS_COMPUTED"])
        self.assertTrue(flags["I29_CORNER_FLUX_RATIONAL"])
        self.assertFalse(flags["I29_REQUIRES_NEW_TRANSCENDENTAL_MASTER"])
        self.assertFalse(flags["COMPLETE_GENERIC_GHOST_DETERMINANT_COMPUTED"])
        self.assertFalse(flags["COMPLETE_REPOSITORY_CUBIC_FORM_FACTORS_ASSEMBLED"])
        self.assertFalse(flags["COMPLETE_RENORMALIZED_Q1_SUPPLIED"])
        self.assertFalse(flags["LORENTZIAN_CERTIFIED"])

    def test_dependency_hashes(self) -> None:
        for reference in self.certificate["dependencies"].values():
            path = ROOT / reference["path"]
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), reference["sha256"])
            self.assertEqual(json.loads(path.read_text())["result_id"], reference["result_id"])


if __name__ == "__main__":
    unittest.main()
