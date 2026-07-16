from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_polar_all_ell_symplectic_restriction import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_all_ell_symplectic_restriction import (
    verify_certificate as verify_independently,
)


class WeylPolarAllEllSymplecticRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_full_off_shell_matrix(self) -> None:
        self.assertEqual(
            self.payload["restriction"]["weyl_maxwell_off_shell_matrix"],
            [["4*(mu-lambda)", "5*lambda-4*mu"], ["5*lambda-4*mu", "4*(mu-lambda)"]],
        )

    def test_branch_ratios_and_signature(self) -> None:
        rows = self.payload["restriction"]["on_shell_branches"]
        self.assertEqual(
            [row["restriction_over_einstein"] for row in rows],
            ["3*sqrt(2)*sqrt(lambda)/2 + 1", "-3*sqrt(2)*sqrt(lambda)/2 + 1"],
        )
        self.assertEqual([row["ell_ge_2_relative_sign"] for row in rows], ["POSITIVE", "NEGATIVE"])
        self.assertEqual(
            self.payload["restriction"]["ell_ge_2_proof"]["signature_relative_to_positive_einstein_branch_form"],
            {"positive": 1, "negative": 1, "zero": 0},
        )

    def test_parity_matching_is_on_shell_only(self) -> None:
        parity = self.payload["restriction"]["parity_comparison"]
        self.assertTrue(parity["axial_and_polar_on_shell_relative_factors_equal"])
        self.assertFalse(parity["off_shell_matrices_equal"])

    def test_mu_zero_and_open_blocks_are_scoped(self) -> None:
        self.assertIn("only the zero field", self.payload["restriction"]["mu_zero_closure"]["verdict"])
        classification = self.payload["classification"]
        self.assertFalse(classification["physical_ell1_and_global_restriction_computed"])
        self.assertFalse(classification["homogeneous_restriction_computed"])
        self.assertFalse(classification["lorentzian_causal_or_scattering_theorem"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
