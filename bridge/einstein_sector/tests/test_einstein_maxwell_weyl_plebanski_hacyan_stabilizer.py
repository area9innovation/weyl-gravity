from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_plebanski_hacyan_stabilizer import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    _rotation_representation,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_plebanski_hacyan_stabilizer import (
    verify_certificate as verify_independently,
)


class PlebanskiHacyanStabilizerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_stabilizer_authority(self) -> None:
        stabilizer = self.payload["background_stabilizer"]
        self.assertEqual(stabilizer["dimension"], 5)
        self.assertFalse(stabilizer["full_SO42_is_background_stabilizer"])
        self.assertEqual(stabilizer["weyl_compensator"], "zero")

    def test_primary_and_pairing_descent(self) -> None:
        primary = self.payload["primary_module_action"]["ideal_preservation"]
        self.assertTrue(primary["Einstein_q_primary_preserved"])
        self.assertTrue(primary["extra_p_primary_preserved"])
        self.assertTrue(self.payload["classification"]["generic_axial_polar_Lee_Wald_invariance_certified"])
        self.assertFalse(self.payload["classification"]["absolute_residual_gauge_quotient_certified"])

    def test_rotation_fixture(self) -> None:
        representation = _rotation_representation(3)
        self.assertEqual(representation["J0"].shape, (7, 7))
        self.assertEqual(representation["Jplus"].T * representation["angular_form"], representation["angular_form"] * representation["Jminus"])

    def test_schema_committed_certificate_and_independent_verifier(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()
        verify_independently()


if __name__ == "__main__":
    unittest.main()
