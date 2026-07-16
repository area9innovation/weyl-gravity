from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate
from bridge.einstein_sector.verify_einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion import verify_certificate as verify_independently


class StandardHarmonicInclusionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_complete_nondegenerate_decomposition(self) -> None:
        table = self.payload["theorem"]["block_table"]
        self.assertEqual(len(table), 4)
        self.assertTrue(all(row["nondegeneracy"] for row in table))
        inclusion = self.payload["theorem"]["inclusion_theorem"]
        self.assertEqual(inclusion["kernel_of_pullback_on_standard_tangent"], "0")
        self.assertFalse(inclusion["identity_inclusion_is_symplectic"])

    def test_interpretive_boundary(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["full_target_observable_embedding_certified"])
        self.assertFalse(classification["final_residual_quotient_computed"])
        self.assertFalse(classification["lorentzian_causal_or_scattering_theorem"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
