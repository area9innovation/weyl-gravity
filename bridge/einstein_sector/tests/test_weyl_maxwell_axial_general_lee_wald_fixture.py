from __future__ import annotations

import hashlib
import json
import unittest

import jsonschema

from bridge.einstein_sector.weyl_maxwell_axial_general_lee_wald_fixture import DEFAULT_OUTPUT, SCHEMA_PATH


class GeneralAxialLeeWaldCommittedFixtureTests(unittest.TestCase):
    """Fast rail; direct tensor regeneration is an affected-chain command."""

    def test_committed_fixture(self) -> None:
        payload = json.loads(DEFAULT_OUTPUT.read_text())
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(payload)
        self.assertEqual(payload["schema_sha256"], hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest())
        self.assertTrue(payload["classification"]["full_four_by_four_coefficient_matrix_checked"])
        self.assertTrue(payload["classification"]["independent_frequencies_checked"])
        self.assertFalse(payload["classification"]["generic_lambda_promotion_in_this_fixture"])


if __name__ == "__main__":
    unittest.main()
