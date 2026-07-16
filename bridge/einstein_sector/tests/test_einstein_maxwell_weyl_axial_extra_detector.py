from __future__ import annotations

import json
import unittest

import jsonschema

from bridge.einstein_sector.einstein_maxwell_weyl_axial_extra_detector import (
    DEFAULT_OUTPUT,
    SCHEMA_PATH,
    build_certificate,
    verify_certificate,
)


class AxialExtraDetectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_certificate()

    def test_schema_and_committed_certificate(self) -> None:
        jsonschema.Draft202012Validator(json.loads(SCHEMA_PATH.read_text())).validate(self.payload)
        self.assertEqual(json.loads(DEFAULT_OUTPUT.read_text()), self.payload)
        verify_certificate()

    def test_detector_reconstructs_extra_coordinates(self) -> None:
        detector = self.payload["detector"]
        self.assertEqual(detector["extra_coordinate_reconstruction"], [["1", "0"], ["0", "1"]])
        self.assertTrue(detector["identity_on_extra_module"])

    def test_detector_kills_Einstein_image(self) -> None:
        detector = self.payload["detector"]
        self.assertEqual(detector["Einstein_image_pairing_remainders"], ["0", "0"])
        self.assertTrue(detector["annihilates_Einstein_image"])

    def test_stronger_observable_claims_stay_open(self) -> None:
        classification = self.payload["classification"]
        self.assertFalse(classification["final_residual_invariance_computed"])
        self.assertFalse(classification["causal_or_asymptotic_observable_constructed"])
        self.assertFalse(classification["particle_or_quantum_observable_constructed"])


if __name__ == "__main__":
    unittest.main()
