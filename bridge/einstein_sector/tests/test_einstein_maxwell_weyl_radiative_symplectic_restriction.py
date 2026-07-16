from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_radiative_symplectic_restriction import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_radiative_symplectic_restriction import (
    verify_certificate as verify_independently,
)


class WeylRadiativeSymplecticRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()

    def test_common_spectral_polynomial(self) -> None:
        theorem = self.payload["theorem"]
        self.assertEqual(theorem["common_spectral_polynomial"], "p_lambda(x)=1+(3/2)*(x-lambda)")
        self.assertIn("p_lambda(M_rad)", theorem["solution_space_identity"])
        for block in theorem["parity_blocks"].values():
            self.assertEqual(block["cross_branch_E_pairing"], "0")
            self.assertEqual(block["cross_branch_target_pairing"], "0")

    def test_combined_signature(self) -> None:
        classification = self.payload["theorem"]["all_ell_ge_2_classification"]
        self.assertEqual(
            classification["branch_coefficient_relative_signature_per_real_spatial_harmonic"],
            {"positive": 2, "negative": 2, "zero": 0},
        )
        self.assertTrue(classification["restricted_target_form_nondegenerate"])
        self.assertFalse(classification["identity_inclusion_preserves_Einstein_symplectic_form"])

    def test_orthogonality_selection_rules_are_explicit(self) -> None:
        proof = self.payload["theorem"]["orthogonality_proof"]
        self.assertIn("equal to its negative", proof["axial_vs_polar"])
        self.assertIn("E-self-adjoint", proof["plus_vs_minus_same_parity"])
        self.assertIn("2*sqrt(2*lambda)>0", proof["frequency_noncollision"])

    def test_real_complex_counting_is_fail_closed(self) -> None:
        counting = self.payload["theorem"]["mode_counting_convention"]
        self.assertIn("not counted as an independent real oscillator", counting["complex_basis"])
        self.assertEqual(counting["oscillators_per_real_spatial_harmonic"], 4)
        self.assertEqual(counting["real_phase_space_dimension_per_q"], "8*q")

    def test_no_quantum_norm_promotion(self) -> None:
        boundary = self.payload["theorem"]["quantum_norm_boundary"]
        self.assertTrue(boundary["classical_relative_symmetric_coefficient_signature_only"])
        self.assertFalse(boundary["positive_frequency_complex_structure_constructed"])
        self.assertFalse(boundary["one_particle_norm_certified"])
        self.assertFalse(boundary["ghost_or_unitarity_theorem"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
