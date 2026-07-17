from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_weyl_polar_offshell_operator_preflight import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate
from bridge.einstein_sector.verify_einstein_weyl_polar_offshell_operator_preflight import verify_certificate as verify_independently


class PolarOffshellOperatorPreflightTests(unittest.TestCase):
    def test_current_certificate(self) -> None:
        verify_certificate(DEFAULT_OUTPUT)

    def test_schema(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(build_certificate())

    def test_independent_verifier(self) -> None:
        verify_independently()

    def test_fail_closed(self) -> None:
        payload = build_certificate()
        self.assertTrue(payload["classification"]["correct_target_polar_field_slice_certified"])
        self.assertFalse(payload["classification"]["full_target_polar_Euler_operator_constructed"])
        self.assertFalse(payload["classification"]["polar_mapping_cofiber_constructed"])


if __name__ == "__main__":
    unittest.main()
