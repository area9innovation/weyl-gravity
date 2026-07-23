from __future__ import annotations

import unittest

from jsonschema import ValidationError

from ..verify_channel_handoff_schema import load_validator


class ChannelHandoffSchemaTest(unittest.TestCase):
    def test_schema_is_valid(self) -> None:
        load_validator()

    def test_empty_document_is_not_a_handoff(self) -> None:
        with self.assertRaises(ValidationError):
            load_validator().validate({})

    def test_unvalidated_status_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            load_validator().validate({
                "schema": "phase3-axial-global-channel-handoff-v1",
                "status": "UNVALIDATED-NUMERIC",
            })

    def test_missing_hminus_contract_is_frozen(self) -> None:
        definition = load_validator().schema["properties"]["missing_Hminus"]
        self.assertEqual(definition["const"]["available"], False)
        self.assertEqual(
            definition["const"]["full_scattering_matrix_constructed"], False
        )


if __name__ == "__main__":
    unittest.main()
