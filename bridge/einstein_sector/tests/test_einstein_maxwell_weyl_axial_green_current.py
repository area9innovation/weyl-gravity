from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_green_current import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate


class AxialGreenCurrentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_reduced_and_ungauged_identities(self) -> None:
        self.assertTrue(self.payload["reduced_current"]["off_shell_identity_verified"])
        self.assertTrue(self.payload["ungauged_current"]["off_shell_identity_verified"])
        self.assertEqual(self.payload["reduced_current"]["jet_identity_remainder"], [])
        self.assertEqual(self.payload["ungauged_current"]["jet_identity_remainder"], [])

    def test_claim_boundary(self) -> None:
        self.assertFalse(self.payload["classification"]["Lee_Wald_pairing_or_particle_claim"])
        self.assertFalse(self.payload["classification"]["Lorentzian_causal_claim"])


if __name__ == "__main__":
    unittest.main()
