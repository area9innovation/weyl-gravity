from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_weyl_relative_linear_triangle_preflight import DEFAULT_OUTPUT, SCHEMA_PATH, build_certificate, verify_certificate
from bridge.einstein_sector.verify_einstein_weyl_relative_linear_triangle_preflight import verify_certificate as verify_independently


class RelativeLinearTrianglePreflightTests(unittest.TestCase):
    def test_generated_certificate_is_current(self) -> None:
        verify_certificate(DEFAULT_OUTPUT)

    def test_schema(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(build_certificate())

    def test_independent_verifier(self) -> None:
        verify_independently()

    def test_fail_closed_global_gate(self) -> None:
        payload = build_certificate()
        self.assertTrue(payload["classification"]["generic_axial_offshell_chain_map_certified"])
        self.assertFalse(payload["classification"]["full_curved_all_sector_chain_map_certified"])
        self.assertFalse(payload["classification"]["quantum_import_gate_satisfied"])


if __name__ == "__main__":
    unittest.main()
