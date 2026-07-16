from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_lee_wald_completion import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate


class AxialLeeWaldCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_direct_match_and_mixed_blocks(self) -> None:
        self.assertTrue(self.payload["direct_current_match"]["generic_direct_match"])
        self.assertTrue(self.payload["classification"]["Einstein_extra_symplectic_orthogonality"])
        self.assertEqual(self.payload["full_solution_pairing"]["mixed_extra_to_Einstein_shell_remainders"], ["0", "0"])

    def test_complete_signature(self) -> None:
        self.assertEqual(self.payload["full_solution_pairing"]["Einstein_branch_signature_for_lambda_ge_6"], [1, 1])
        self.assertEqual(self.payload["full_solution_pairing"]["extra_branch_signature_for_lambda_ge_6"], [2, 0])
        self.assertEqual(self.payload["full_solution_pairing"]["complete_generic_axial_target_signature"], [3, 1])

    def test_quantum_claim_remains_fail_closed(self) -> None:
        self.assertFalse(self.payload["classification"]["positive_frequency_Hilbert_space_or_particle_claim"])
        self.assertFalse(self.payload["classification"]["quantum_ghost_or_unitarity_claim"])
        self.assertFalse(self.payload["classification"]["Lorentzian_causal_claim"])


if __name__ == "__main__":
    unittest.main()
