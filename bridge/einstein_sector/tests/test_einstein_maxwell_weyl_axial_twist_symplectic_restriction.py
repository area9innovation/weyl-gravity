from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_twist_symplectic_restriction import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate
from bridge.einstein_sector.verify_einstein_maxwell_weyl_axial_twist_symplectic_restriction import verify_certificate as verify_independently


class AxialTwistRestrictionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_factor_minus_two_and_rank(self) -> None:
        forms = self.payload["theorem"]["cauchy_forms_after_common_factor_L_N_1m"]
        self.assertEqual(forms["identity"], "Omega_WM|twist=-2*Omega_EM|twist")
        self.assertEqual(forms["target_rank"], 2)
        self.assertEqual(self.payload["theorem"]["mode_counting"]["darboux_pairs"], 3)

    def test_exceptional_and_claim_boundary(self) -> None:
        self.assertFalse(self.payload["classification"]["radiative_mu_zero_continuation_used"])
        self.assertFalse(self.payload["classification"]["one_particle_or_quantum_theorem"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
