"""Tests for the BT separable lowest-mode curvature certificate."""

from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest

from reverse_physics.bt_euclidean_separable_lowest_mode_curvature import CERT_PATH, build
from reverse_physics.verify_bt_euclidean_separable_lowest_mode_curvature import verify


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        with open(CERT_PATH, encoding="utf-8") as handle:
            self.payload = json.load(handle)

    def mutate(self, function) -> None:
        changed = copy.deepcopy(self.payload)
        function(changed)
        descriptor, path = tempfile.mkstemp(suffix=".json")
        os.close(descriptor)
        try:
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(changed, handle)
            self.assertFalse(verify(path))
        finally:
            os.unlink(path)

    def test_deterministic_builder(self) -> None:
        self.assertEqual(self.payload, build())

    def test_independent_verifier(self) -> None:
        self.assertTrue(verify())

    def test_rejects_fixture_mutation(self) -> None:
        self.mutate(lambda data: data["exact_correlated_fixture"]["spatial_correlation_remainder_per_inert_spatial_cell"].__setitem__("numerator", 1))

    def test_rejects_scope_promotion(self) -> None:
        self.mutate(lambda data: data["method_disposition"].__setitem__("all_background_recentered_conditional_variance", "PROVED"))

    def test_rejects_h_minus_one_promotion(self) -> None:
        self.mutate(lambda data: data["method_disposition"].__setitem__("actual_interacting_h_minus_one_second_moment", "PROVED"))

    def test_rejects_extra_field(self) -> None:
        self.mutate(lambda data: data.__setitem__("claim", "too broad"))


if __name__ == "__main__":
    unittest.main()
