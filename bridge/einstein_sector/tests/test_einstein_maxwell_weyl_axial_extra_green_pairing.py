from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_green_pairing import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate


class AxialExtraGreenPairingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_nonradical_physical_pairing(self) -> None:
        self.assertTrue(self.payload["pairing"]["nondegenerate_for_all_physical_ell_ge_2"])
        self.assertEqual(self.payload["pairing"]["physical_sign_check"]["signature"], [2, 0])

    def test_physical_claim_remains_fail_closed(self) -> None:
        self.assertFalse(self.payload["classification"]["direct_four_dimensional_Lee_Wald_match"])
        self.assertFalse(self.payload["classification"]["physical_norm_or_ghost_claim"])
        self.assertFalse(self.payload["classification"]["particle_claim"])


if __name__ == "__main__":
    unittest.main()
