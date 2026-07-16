from __future__ import annotations

import json
import unittest

import jsonschema
import sympy as sp

from bridge.einstein_sector.einstein_maxwell_weyl_axial_quadratic_channel_preflight import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    _resonance_polynomial_terms,
    _terms_expression,
    build_certificate,
    verify_certificate,
)


class AxialQuadraticChannelPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_exact_finite_resonance_ledger(self) -> None:
        ledger = self.payload["parity_and_resonance_ledger"]
        self.assertEqual(ledger["temporal_sign_and_branch_cases_scanned"], 97848)
        self.assertEqual(ledger["exact_resonances"], [])
        self.assertTrue(ledger["no_exact_resonance_in_window"])

    def test_radical_canonicalizer_matches_direct_expression(self) -> None:
        for labels in ((2, 4, 6, -3, 0, -1, -1), (2, 2, 2, 0, 0, -1, -1), (3, 5, 4, 2, -1, 1, -1)):
            ell_a, ell_p, ell_x, k_a, k_p, branch_a, branch_p = labels
            lambda_a = ell_a * (ell_a + 1)
            lambda_p = ell_p * (ell_p + 1)
            lambda_x = ell_x * (ell_x + 1)
            A = k_a**2 + lambda_a + branch_a * sp.sqrt(2 * lambda_a)
            B = k_p**2 + lambda_p + branch_p * sp.sqrt(2 * lambda_p)
            C = (k_a + k_p) ** 2 + lambda_x - sp.Rational(2, 3)
            direct = sp.expand((C - A - B) ** 2 - 4 * A * B)
            canonical = _terms_expression(_resonance_polynomial_terms(*labels))
            self.assertEqual(sp.simplify(direct - canonical), 0)

    def test_first_block_is_removable_but_source_remains_open(self) -> None:
        block = self.payload["first_EE_block"]
        self.assertTrue(block["inverse_identity_verified"])
        self.assertFalse(block["source_tensor_coefficient_computed"])
        self.assertIn("NOT_APPLICABLE", block["normal_extra_shell_projection"])

    def test_no_general_closure_promotion(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["general_nonlinear_Einstein_sector_closed"])
        self.assertFalse(classification["all_harmonics_resonance_free"])


if __name__ == "__main__":
    unittest.main()
