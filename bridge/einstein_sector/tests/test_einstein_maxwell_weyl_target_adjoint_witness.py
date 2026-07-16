from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_target_adjoint_witness import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)


class TargetAdjointWitnessTests(unittest.TestCase):
    def test_schema_certificate_and_domain(self) -> None:
        payload = build_certificate()
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), payload)
        verify_certificate()
        self.assertTrue(payload["classification"]["standalone_target_domain_witness"])
        self.assertFalse(payload["classification"]["complete_spacetime_formal_adjoint_cokernel"])

    def test_temporal_spaces_do_not_change_constraint_witness(self) -> None:
        payload = build_certificate()
        self.assertIn("both spaces", payload["temporal_correction_spaces"]["constant_lapse_verdict"])


if __name__ == "__main__":
    unittest.main()
