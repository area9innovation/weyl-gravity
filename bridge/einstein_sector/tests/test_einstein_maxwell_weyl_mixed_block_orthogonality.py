from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_mixed_block_orthogonality import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate
from bridge.einstein_sector.verify_einstein_maxwell_weyl_mixed_block_orthogonality import verify_certificate as verify_independently


class MixedBlockOrthogonalityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_shared_label_collision(self) -> None:
        direct = self.payload["theorem"]["direct_shared_label_collision"]
        self.assertEqual(direct["exact_off_shell_factor"], "omega^2-4")
        self.assertEqual(direct["on_shell_value"], "0")
        self.assertTrue(direct["both_twist_Jordan_coordinates_included"])

    def test_complete_mixed_matrix(self) -> None:
        self.assertTrue(self.payload["classification"]["all_standard_mixed_blocks_zero"])
        self.assertFalse(self.payload["classification"]["extra_fourth_order_target_mixed_pairing_computed"])

    def test_independent_verifier(self) -> None:
        self.assertEqual(verify_independently()["result_id"], self.payload["result_id"])


if __name__ == "__main__":
    unittest.main()
