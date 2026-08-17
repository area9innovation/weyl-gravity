"""Falsification tests for the BT torus top-band flow theorem."""

from __future__ import annotations

import copy
import json
import unittest

from reverse_physics.bt_euclidean_torus_top_band_flow import build
from reverse_physics.verify_bt_euclidean_torus_top_band_flow import (
    DEFAULT_CERTIFICATE,
    verify,
)


class TorusTopBandFlowTests(unittest.TestCase):
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

    def test_fixture_checks_close(self) -> None:
        self.assertTrue(all(self.certificate["exact_fixture"]["checks"].values()))

    def test_mutated_error_norm_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["exact_fixture"]["error_edge_norm_squared"].__setitem__(
                "numerator", data["exact_fixture"]["error_edge_norm_squared"]["numerator"] + 1
            )
        )

    def test_mutated_top_condition_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["top_band_theorem"].__setitem__(
                "hypothesis", "W^2>=128*q^3*D^2*N*F"
            )
        )

    def test_mutated_cutoff_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_dichotomy"].__setitem__(
                "torus_sufficient_condition", "W>=1024*L^(11/3)"
            )
        )

    def test_mutated_normalized_floor_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["four_torus_dichotomy"].__setitem__(
                "normalized_conclusion", "Q/omega_L^2>=1"
            )
        )

    def test_false_all_field_promotion_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "all_field_torus_scaled_PL", "PROVED"
            )
        )

    def test_closed_multiband_gate_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["research_disposition"].__setitem__(
                "moderate_sparse_multiband_sector", "CLOSED"
            )
        )

    def test_mutated_input_hash_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["provenance"]["inputs"][0].__setitem__("sha256", "0" * 64)
        )

    def test_lorentzian_tag_is_rejected(self) -> None:
        self.assert_rejected(
            lambda data: data["dependency_tags"].append("LORENTZIAN-CAUSAL")
        )


if __name__ == "__main__":
    unittest.main()
