from __future__ import annotations

import json
import unittest

from jsonschema import Draft202012Validator

from bridge.einstein_sector.einstein_weyl_relative_residual_action_descent import (
    OUTPUT,
    OVERLAY,
    SCHEMA,
    build_certificate,
    build_overlay,
    verify_outputs,
)
from bridge.einstein_sector.verify_einstein_weyl_relative_residual_action_descent import (
    verify_certificate as verify_independently,
)


class RelativeResidualActionDescentTests(unittest.TestCase):
    def test_generated_outputs_are_current(self) -> None:
        verify_outputs()

    def test_schema(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(build_certificate())

    def test_independent_consumer(self) -> None:
        verify_independently()

    def test_fail_closed_overlay(self) -> None:
        certificate = json.loads(OUTPUT.read_text(encoding="utf-8"))
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        self.assertEqual(overlay, build_overlay(certificate))
        self.assertTrue(overlay["generated_claims_ledger"])
        for row in overlay["rows"]:
            self.assertEqual(row["cells"]["global_orbit_quotient"]["status"], "NO_CERTIFIED_MAP")
            self.assertEqual(row["cells"]["causal_green_descent"]["status"], "NO_CERTIFIED_MAP")


if __name__ == "__main__":
    unittest.main()
