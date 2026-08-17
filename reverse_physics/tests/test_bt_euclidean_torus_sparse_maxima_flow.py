"""Falsification tests for the BT torus sparse-maxima flow theorem."""

from __future__ import annotations

import copy
import json
import os
import unittest

from reverse_physics.bt_euclidean_torus_sparse_maxima_flow import build
from reverse_physics.verify_bt_euclidean_torus_sparse_maxima_flow import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusSparseMaximaFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open(DEFAULT_CERTIFICATE, encoding="utf-8") as handle:
            cls.certificate = json.load(handle)

    def assert_rejected(self, mutation) -> None:
        candidate = copy.deepcopy(self.certificate)
        mutation(candidate)
        self.assertFalse(all(passed for _, passed in verify(candidate)))

    def test_generated_certificate_matches(self) -> None:
        self.assertEqual(build(), self.certificate)

    def test_unmodified_certificate_passes(self) -> None:
        self.assertTrue(all(passed for _, passed in verify(self.certificate)))

    def test_exact_fixtures_clear_theorem(self) -> None:
        for row in self.certificate["exact_fixtures"]:
            self.assertGreaterEqual(
                row["condition_left_WF"]["numerator"]
                * row["condition_right_24q2DN"]["denominator"],
                row["condition_right_24q2DN"]["numerator"]
                * row["condition_left_WF"]["denominator"],
            )
            self.assertTrue(all(row["checks"].values()))

    def test_mutated_fixture_norm_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixtures"][0]["gradient_norm_squared"].__setitem__(
                "numerator", data["exact_fixtures"][0]["gradient_norm_squared"]["numerator"] + 1
            )
        )

    def test_mutated_theorem_constant_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["theorem"].__setitem__("hypothesis", "W*F>=12*q^2*D*N")
        )

    def test_mutated_density_corollary_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_corollary"].__setitem__(
                "near_maximal_count", "E_theta<=2*F/theta^2"
            )
        )

    def test_false_all_field_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "all_field_torus_scaled_PL", "PROVED"
            )
        )

    def test_lorentzian_tag_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )

    def test_mutated_predecessor_hash_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64)
        )

    def test_open_multiband_gate_is_required(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "dense_multiband_polynomial_contrast_sector", "CLOSED"
            )
        )

    def test_certificate_path_exists(self) -> None:
        self.assertTrue(os.path.isfile(DEFAULT_CERTIFICATE))


if __name__ == "__main__":
    unittest.main()
