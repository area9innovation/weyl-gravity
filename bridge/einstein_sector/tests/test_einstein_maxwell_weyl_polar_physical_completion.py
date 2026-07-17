from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_polar_physical_completion import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    _normalization_audit,
    _physical_ring_audit,
    _primary_image_audit,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_physical_completion import verify_certificate as verify_independently


class PolarPhysicalCompletionTests(unittest.TestCase):
    def test_action_normalization(self) -> None:
        audit = _normalization_audit()
        self.assertEqual(audit["derived_row_weights"], ["-1", "2", "-1", "2*lambda"])
        self.assertTrue(audit["identity_verified"])

    def test_physical_ring_and_primary_image(self) -> None:
        ring = _physical_ring_audit()
        self.assertEqual(
            ring["determinantal_ideals_over_R_phys_P_omega"]["invariant_factors_on_every_physical_fiber"],
            ["1", "1", "p", "p*q"],
        )
        self.assertTrue(ring["zero_momentum_audit"]["zero_momentum_retained"])
        self.assertTrue(_primary_image_audit()["Einstein_image_equals_complete_q_primary_summand"])

    def test_current_certificate_and_schema(self) -> None:
        payload = json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(payload)
        verify_certificate(DEFAULT_OUTPUT)
        verify_independently()


if __name__ == "__main__":
    unittest.main()
