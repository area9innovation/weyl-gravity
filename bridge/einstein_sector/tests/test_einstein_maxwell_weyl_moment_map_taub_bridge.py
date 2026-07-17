from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_moment_map_taub_bridge import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)
from bridge.einstein_sector.verify_einstein_maxwell_weyl_moment_map_taub_bridge import (
    verify_certificate as verify_independently,
)


class MomentMapTaubBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_three_normalization_calibrations(self) -> None:
        calibration = self.payload["normalization_calibration"]
        self.assertTrue(calibration["extra_axial"]["exact_match"])
        self.assertTrue(calibration["Einstein_minus_axial"]["exact_match"])
        self.assertTrue(calibration["Einstein_minus_polar"]["exact_match"])

    def test_generic_extra_no_go(self) -> None:
        classification = self.payload["classification"]
        self.assertTrue(classification["generic_extra_H_Taub_negative_definite"])
        self.assertTrue(classification["all_nonzero_generic_pure_extra_fixed_bundle_tangents_second_order_obstructed"])
        self.assertEqual(
            self.payload["extension_verdict"]["pure_generic_extra_fixed_bundle"],
            "NO_NONZERO_REAL_TANGENT_EXTENDS_TO_SECOND_ORDER",
        )

    def test_boundaries_remain_fail_closed(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["mixed_Einstein_extra_zero_locus_classified"])
        self.assertFalse(classification["exceptional_global_moment_maps_classified"])
        self.assertFalse(classification["absolute_stabilizer_quotient_certified"])
        self.assertFalse(classification["cyclic_BV_enhancement_certified"])

    def test_schema_committed_certificate_and_independent_verifier(self) -> None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text(encoding="utf-8")), self.payload)
        verify_certificate()
        verify_independently()


if __name__ == "__main__":
    unittest.main()
