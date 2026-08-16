"""Tests for the BT pair-block g4 L6 certified interval."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_pair_block_response_g4_l6_interval import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_pair_block_response_g4_l6_interval import (
    platform_probe,
    verify,
)


class IntervalCertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def test_platform_probe(self) -> None:
        self.assertTrue(platform_probe())

    def test_deterministic_builder(self) -> None:
        self.assertEqual(build(), self.certificate)

    def test_independent_verifier(self) -> None:
        self.assertTrue(verify(CERT_PATH))

    def assert_mutation_rejected(self, mutate) -> None:
        changed = copy.deepcopy(self.certificate)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        try:
            mutate(changed)
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_mutation_negative_total(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["coefficient"]["total"].__setitem__("midpoint", "-0.001")
        )

    def test_mutation_shrunken_calibration(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["calibration"]["b2"]["computed_interval"].__setitem__("radius", "1e-30")
        )

    def test_mutation_large_volume_promotion(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["method_disposition"].__setitem__("large_volume_g4_power_or_log", "BOUNDED")
        )

    def test_mutation_lorentzian_tag(self) -> None:
        self.assert_mutation_rejected(lambda cert: cert["dependency_tags"].append("LORENTZIAN-CAUSAL"))

    def test_mutation_exact_type(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["coefficient"].__setitem__("numeric_type", "EXACT_RATIONAL")
        )

    def test_mutation_input_hash(self) -> None:
        self.assert_mutation_rejected(
            lambda cert: cert["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64)
        )


if __name__ == "__main__":
    unittest.main()
