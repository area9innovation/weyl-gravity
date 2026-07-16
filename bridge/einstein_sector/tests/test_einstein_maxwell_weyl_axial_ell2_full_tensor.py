from __future__ import annotations

import json
import hashlib
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_ell2_full_tensor import DEFAULT_OUTPUT, SCHEMA_PATH


class AxialEll2FullTensorCommittedFixtureTests(unittest.TestCase):
    """Fast rail; the exhaustive tensor regeneration is a separate command."""

    def test_committed_fixture_schema_and_claim_boundary(self) -> None:
        payload = json.loads(DEFAULT_OUTPUT.read_text())
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(payload)
        self.assertEqual(payload["schema_sha256"], hashlib.sha256(SCHEMA_PATH.read_bytes()).hexdigest())
        self.assertTrue(payload["classification"]["ell2_full_tensor_replay_passed"])
        self.assertTrue(payload["classification"]["all_unlisted_rows_zero"])
        self.assertFalse(payload["classification"]["Green_identity_or_particle_claim"])


if __name__ == "__main__":
    unittest.main()
