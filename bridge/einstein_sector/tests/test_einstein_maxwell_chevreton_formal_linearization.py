from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_chevreton_formal_linearization import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_chevreton_formal_linearization import (
    verify_certificate as verify_independently,
)


class ChevretonFormalLinearizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_all_jacobi_fields_are_covered(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["all_formal_linearized_Einstein_Maxwell_solutions_included"])
        self.assertFalse(classification["only_integrable_tangents"])

    def test_parallel_flux_kills_linear_chevreton_term(self) -> None:
        self.assertIn("DC_Ch", self.payload["proof"]["parallel_flux_consequence"])
        self.assertEqual(
            self.payload["formal_audit"]["symbolic_dual_remainder_checks"]["quadratic_first_jet"],
            "0",
        )

    def test_stronger_off_shell_claim_fails_closed(self) -> None:
        self.assertFalse(self.payload["classification"]["off_shell_BV_chain_map_constructed"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
