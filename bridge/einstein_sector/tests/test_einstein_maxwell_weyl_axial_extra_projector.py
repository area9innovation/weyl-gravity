from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_projector import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)


class AxialExtraProjectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_projector_identities(self) -> None:
        projector = self.payload["projector"]
        self.assertTrue(projector["basis_independent"])
        self.assertTrue(projector["identity_on_extra_module"])
        self.assertEqual(projector["rank"], 2)
        self.assertEqual(projector["idempotence_remainder"], [["0"] * 4 for _ in range(4)])

    def test_off_shell_claim_stays_open(self) -> None:
        self.assertFalse(self.payload["classification"]["off_shell_projector"])


if __name__ == "__main__":
    unittest.main()
